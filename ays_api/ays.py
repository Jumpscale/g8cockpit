from flask import Blueprint as fBlueprint, jsonify, request, json, Response, current_app
from JumpScale import j
from JumpScale.core.errorhandling.JSExceptions import BaseJSException
from .views import service_view, template_view, blueprint_view, repository_view, run_view
from threading import Lock

from .Repository import Repository
from .Blueprint import Blueprint
from .Actor import Actor
from .ActorRepo import ActorRepo


ays_api = fBlueprint('ays_api', __name__)
logger = j.logger.get('j.app.cockpit.api')

AYS_REPO_DIR = '/optvar/cockpit_repos'

ays_cfg_lock = Lock()

# create client to AYS daemon
daemon_client = j.clients.atyourservice.get(
    host=j.atyourservice.config['redis'].get('host'),
    port=j.atyourservice.config['redis'].get('port'),
    unixsocket=j.atyourservice.config['redis'].get('unixsocket'))


def get_repo(name):
    """
    try to get a repo by his name.
    name is prepend with AYS_REPO_DIR to create the full path to the repo
    raise j.exceptions.NotFound if repo doesn't exists
    """
    path = j.sal.fs.joinPaths(AYS_REPO_DIR, name)
    res = j.atyourservice._repos.find(path=path)
    if len(res) <= 0:
        raise j.exceptions.NotFound(
            "Repository {} doesn't exists".format(name))
    if len(res) > 1:
        raise j.exceptions.BUG(
            "More then one repository find with this name ({}). this should not happen.".format(name))
    return res[0].objectGet()

# Repository endpoints


@ays_api.route('/ays/repository', methods=['GET'])
def listRepositories():
    '''
    list all repositorys
    It is handler for GET /ays/repository
    '''
    repos = [repository_view(repo) for repo in j.atyourservice.reposList()]
    return json.dumps(repos), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository', methods=['POST'])
def createNewRepository():
    '''
    create a new repository
    It is handler for POST /ays/repository
    '''
    data = json.loads(request.data)
    inputs = Repository.from_json(data)
    if not inputs.validate():
        return jsonify(errors=inputs.errors), 400

    name = inputs.name.data
    git_url = inputs.git_url.data
    try:
        _ = get_repo(name)
        return jsonify(error='AYS Repository "%s" already exsits' % name), 409
    except j.exceptions.NotFound:
        pass

    path = j.sal.fs.joinPaths(AYS_REPO_DIR, name)
    try:
        j.atyourservice.repoCreate(path, git_url=git_url)
    except Exception as err:
        # clean directory if something went wrong during creation
        if j.sal.fs.exists(path):
            j.sal.fs.removeDirTree(path)
        raise err


    return jsonify(name=name, path=path, git_url=git_url), 201


@ays_api.route('/ays/repository/<repository>', methods=['GET'])
def getRepository(repository):
    '''
    Get information of a repository
    It is handler for GET /ays/repository/<repository>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    return jsonify(name=repo.name, path=repo.path)


@ays_api.route('/ays/repository/<repository>', methods=['DELETE'])
def deleteRepository(repository):
    '''
    Delete a repository
    It is handler for DELETE /ays/repository/<repository>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    repo.destroy()
    if j.sal.fs.exists(repo.path):
        j.sal.fs.removeDirTree(repo.path)

    return '', 204


# Blueprint endpoints
@ays_api.route('/ays/repository/<repository>/blueprint', methods=['GET'])
def listBlueprints(repository):
    '''
    List all blueprint
    It is handler for GET /ays/repository/<repository>/blueprint
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    include_archived = j.data.types.bool.fromString(request.args.get('archived', 'True'))

    blueprints = []

    for blueprint in repo.blueprints:
        blueprints.append(blueprint_view(blueprint))

    if include_archived:
        for blueprint in repo.blueprintsDisabled:
            blueprints.append(blueprint_view(blueprint))

    return json.dumps(blueprints), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/blueprint', methods=['POST'])
def createNewBlueprint(repository):
    '''
    Create a new blueprint
    It is handler for POST /ays/repository/<repository>/blueprint
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    inputs = Blueprint.from_json(request.json)
    if not inputs.validate():
        return jsonify(errors=inputs.errors), 400

    new_name = inputs.name.data
    content = inputs.content.data

    names = [bp.name for bp in repo.blueprints]
    if new_name in names:
        return jsonify(error="Blueprint with the name %s' already exists" % new_name), 409

    # check validity of input as YAML syntax
    try:
        j.data.serializer.yaml.loads(content)
    except:
        return jsonify(error="Invalid YAML syntax"), 400

    bp_path = j.sal.fs.joinPaths(repo.path, 'blueprints', new_name)
    try:
        j.sal.fs.writeFile(bp_path, content)
        blueprint = repo.blueprintGet(bp_path)
    except:
        if j.sal.fs.exists(bp_path):
            j.sal.fs.remove(bp_path)
        return jsonify(error="Can't save new blueprint"), 500

    # check validity of input as blueprint syntax
    try:
        blueprint.validate()
    except:
        if j.sal.fs.exists(bp_path):
            j.sal.fs.remove(bp_path)
        return jsonify(error="Invalid blueprint syntax"), 400

    return jsonify(blueprint_view(blueprint)), 201


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>', methods=['PUT'])
def updateBlueprint(blueprint, repository):
    '''
    Update existing blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    inputs = Blueprint.from_json(request.json)
    if not inputs.validate():
        return jsonify(error=inputs.errors), 400

    name = inputs.name.data
    content = inputs.content.data

    names = [bp.name for bp in repo.blueprints]
    names.extend([bp.name for bp in repo.blueprintsDisabled])
    if name not in names:
        return jsonify(error="blueprint with the name %s not found" % name), 404

    blueprint_path = j.sal.fs.joinPaths(repo.path, 'blueprints', name)
    blueprint = repo.blueprintGet(blueprint_path)
    blueprint.content = content
    j.sal.fs.writeFile(blueprint_path, content)

    return json.dumps(blueprint_view(blueprint)), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>/archive', methods=['PUT'])
def archiveBlueprint(blueprint, repository):
    '''
    Archive existing blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>/archive
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    by_names = {bp.name: bp for bp in repo.blueprints}
    if blueprint not in by_names:
        return jsonify(error="blueprint with the name %s not found" % blueprint), 404

    by_names[blueprint].disable()

    return jsonify(msg='Blueprint %s archived' % blueprint), 200


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>/restore', methods=['PUT'])
def restoreBlueprint(blueprint, repository):
    '''
    Restore archived blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>/restore
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    by_names = {bp.name: bp for bp in repo.blueprintsDisabled}
    if blueprint not in by_names:
        return jsonify(error="blueprint with the name %s not found" % blueprint), 404

    by_names[blueprint].enable()

    return jsonify(msg='Blueprint %s restored' % blueprint), 200


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>', methods=['GET'])
def getBlueprint(blueprint, repository):
    '''
    Get a blueprint
    It is handler for GET /ays/repository/<repository>/blueprint/<blueprint>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    bp = None
    for item in repo.blueprints:
        if item.name == blueprint:
            bp = item
            break
    else:
        return jsonify(error="No blueprint found with this name '%s'" % blueprint), 404

    return json.dumps(blueprint_view(bp)), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>', methods=['POST'])
def executeBlueprint(blueprint, repository):
    '''
    Execute the blueprint
    It is handler for POST /ays/repository/<repository>/blueprint/<blueprint>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    bp = None
    for item in repo.blueprints:
        if item.name == blueprint:
            bp = item
            break
    else:
        return jsonify(error="No blueprint found with this name '%s'" % blueprint), 404

    try:
        repo.blueprintExecute(path=bp.path, role='', instance='')

        # notify bot new services have been created
        # TODO: unify event for telegram and REST
        # evt = j.data.models.cockpit_event.Telegram()
        # evt.io = 'input'
        # evt.action = 'bp.create'
        # evt.args = {
        #     'path': bp.path,
        #     'content': bp.content,
        # }
        # j.core.db.publish('telegram', evt.to_json())

    except Exception as e:
        error_msg = "Error during execution of the blueprint:\n %s" % str(e)
        logger.error(error_msg)
        return jsonify(error=error_msg), 500

    return jsonify(msg="Blueprint %s executed" % blueprint)


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>', methods=['DELETE'])
def deleteBlueprint(blueprint, repository):
    '''
    delete blueprint
    It is handler for DELETE /ays/repository/<repository>/blueprint/<blueprint>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 4044

    by_names = {bp.name: bp for bp in repo.blueprints}
    for bp in repo.blueprintsDisabled:
        by_names[bp.name] = bp

    if blueprint not in by_names:
        return jsonify(error="blueprint with the name %s not found" % blueprint), 404

    bp = by_names[blueprint]

    if j.sal.fs.exists(bp.path):
        j.sal.fs.remove(bp.path)

    return jsonify(), 204


# Service endpoints
@ays_api.route('/ays/repository/<repository>/service', methods=['GET'])
def listServices(repository):
    '''
    List all services in the repository
    It is handler for GET /ays/repository/<repository>/service
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    services = []
    for s in repo.services:
        services.append(service_view(s))

    services = sorted(services, key=lambda service: service['role'])

    return json.dumps(services), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/service/<role>', methods=['GET'])
def listServicesByRole(role, repository):
    '''
    List all services of role 'role' in the repository
    It is handler for GET /ays/repository/<repository>/service/<role>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    services = []
    for s in repo.servicesFind(actor='%s.*' % role):
        services.append(service_view(s))

    services = sorted(services, key=lambda service: service['role'])

    return json.dumps(services), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/service/<role>/<name>', methods=['GET'])
def serviceGetByName(name, role, repository):
    '''
    Get a service instance
    It is handler for GET /ays/repository/<repository>/service/<role>/<instance>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    s = repo.serviceGet(role=role, instance=name, die=False)
    if s is None:
        return jsonify(error='Service not found'), 404

    service = service_view(s)

    return json.dumps(service), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/service/<role>/<name>', methods=['DELETE'])
def deleteServiceByName(name, role, repository):
    '''
    delete a servicea and all its children'
    It is handler for DELETE /ays/repository/<repository>/service/<role>/<instance>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    service = repo.serviceGet(role=role, instance=name, die=False)
    if service is None:
        return jsonify(error='Service role:%s name:%s not found in the repo %s' % (role, name, repository)), 404

    service.delete()

    return jsonify(), 204


# Template endpoints
@ays_api.route('/ays/repository/<repository>/template', methods=['GET'])
def listTemplates(repository):
    '''
    list all templates
    It is handler for GET /ays/repository/<repository>/template
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    templates = [k for k in repo.templates.keys()]

    templates = sorted(templates, key=lambda template: template)

    return json.dumps(templates), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/template/<template>', methods=['GET'])
def getTemplate(template, repository):
    '''
    Get a template
    It is handler for GET /ays/repository/<repository>/template/<template>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    template_names = list(repo.templates.keys())
    if template not in template_names:
        return jsonify(error="template not found"), 404

    tmpl = repo.templates[template]
    template = template_view(tmpl)
    return json.dumps(template), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/template', methods=['POST'])
def addTemplateRepo():
    '''
    add a new service template repository
    It is handler for POST /ays/template
    '''

    inputs = ActorRepo.from_json(request.json)
    if not inputs.validate():
        return jsonify(errors=inputs.errors), 400

    url = inputs.url.data
    branch = inputs.branch.data or "master"

    if url == '':
        return jsonify(error="URL can't be empty"), 400

    if url.endswith('.git'):
        url = url[:-len('.git')]

    cfg_path = j.sal.fs.joinPaths(j.dirs.cfgDir, 'ays/ays.conf')

    # single thread access to prevent race condition on config file
    with ays_cfg_lock:
        cfg = j.data.serializer.toml.load(cfg_path)

        metadata = cfg['metadata']
        urls = []
        for md in metadata:
            urls.extend([m['url'] for m in md.values()])

        if url in urls:
            return jsonify(url=url, branch=branch), 201

        name = url.split('/')[-1]
        template = {
            'branch': branch,
            'url': url
        }
        metadata.append({name: template})
        j.data.serializer.toml.dump(cfg_path, cfg)

    return jsonify(url=url, branch=branch), 201

# Runs endpoint


@ays_api.route('/ays/repository/<repository>/aysrun', methods=['GET'])
def listRuns(repository):
    '''
    list all runs of the repository
    It is handler for GET /ays/repository/<repository>/aysrun
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    runs = repo.runsList()
    runs = [run_view(run) for run in runs]
    return json.dumps(runs), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/aysrun/<aysrun>', methods=['GET'])
def getRun(aysrun, repository):
    '''
    Get an aysrun
    It is handler for GET /ays/repository/<repository>/aysrun/<aysrun>
    '''
    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    aysrun_model = repo.runGet(aysrun)
    aysrun = aysrun_model.objectGet()

    return json.dumps(run_view(aysrun)), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/aysrun', methods=['POST'])
def createRun(repository):
    '''
    create a run and execute it
    It is handler for POST /ays/repository/<repository>/aysrun
    '''

    try:
        repo = get_repo(repository)
    except j.exceptions.NotFound as e:
        return jsonify(error=e.message), 404

    simulate = j.data.types.bool.fromString(request.args.get('simulate', 'False'))
    callback_url = request.args.get('callback_url', None)

    try:
        run = repo.runCreate()
        run.save()
        if not simulate:
            daemon_client.execute_run(run=run, callback_url=callback_url)

        return json.dumps(run_view(run.model)), 200, {'Content-Type': 'application/json'}

    except j.exceptions.Input as e:
        return jsonify(error=e.msgpub), 500
    except Exception as e:
        return jsonify(error="Unexpected error: %s" % str(e)), 500
