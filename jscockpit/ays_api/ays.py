from flask import Blueprint as fBlueprint, jsonify, request, json, Response, current_app
from JumpScale import j
from JumpScale.baselib.atyourservice81.Blueprint import Blueprint as JSBlueprint
from JumpScale.core.errorhandling.JSExceptions import BaseJSException
from .views import service_view, actor_view, blueprint_view, repository_view, run_view

from .Repository import Repository
from .Blueprint import Blueprint
from .Template import Template
from .TemplateRepo import TemplateRepo


ays_api = fBlueprint('ays_api', __name__)
logger = j.logger.get('j.app.cockpit.api')

AYS_REPO_DIR = j.sal.fs.joinPaths(j.dirs.codeDir, 'github', 'jumpscale', 'jumpscale_ays8_testenv')


@ays_api.route('/ays/reload', methods=['GET'])
def reloadAll():
    current_app.ays_bot.reload_all()
    return jsonify(msg='reload done'), 200


@ays_api.route('/ays/repository', methods=['GET'])
def listRepositories():
    '''
    list all repositorys
    It is handler for GET /ays/repository
    '''
    repos = j.atyourservice.reposDiscover()
    repos = [repo.__str__() for repo in repos]
    return json.dumps(repos), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository', methods=['POST'])
def createNewRepository():
    '''
    create a new repository
    It is handler for POST /ays/repository
    '''
    j.atyourservice.reposDiscover()
    data = json.loads(request.data)
    inputs = Repository.from_json(data)
    if not inputs.validate():
        return jsonify(errors=inputs.errors), 400

    name = inputs.name.data
    if j.atyourservice._repos.get(name, False):
        return jsonify(error='AYS Repository "%s" already exsits' % name), 409

    path = j.sal.fs.joinPaths(AYS_REPO_DIR, name)
    j.atyourservice.repoCreate(path)
    return jsonify(name=name, path=path), 201


@ays_api.route('/ays/repository/<repository>', methods=['GET'])
def getRepository(repository):
    '''
    Get information of a repository
    It is handler for GET /ays/repository/<repository>
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, False)
    if not repo:
        return jsonify(error='Repository %s not found' % repository), 404

    return jsonify(name=repo.name, path=repo.path)


@ays_api.route('/ays/repository/<repository>', methods=['DELETE'])
def deleteRepository(repository):
    '''
    Delete a repository
    It is handler for DELETE /ays/repository/<repository>
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, False)

    if not repo:
        return jsonify(error='Repository %s not found' % repository), 404

    repo.destroy()
    if j.sal.fs.exists(repo.path):
        j.sal.fs.removeDirTree(repo.path)

    return '', 204


@ays_api.route('/ays/repository/<repository>/init', methods=['POST'])
def initRepository(repository):
    '''
    Init a repository
    It is handler for POST /ays/repository/<repository>/init
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    role = request.args.get('role', '')
    instance = request.args.get('instance', '')

    try:
        repo.init(role=role, instance=instance)
    except Exception as e:
        error_msg = "Error during execution of init on repository %s:\n %s" % (repo.name, str(e))
        logger.error(error_msg)
        return jsonify(error=error_msg), 500

    return jsonify(msg="Blueprint %s initialized" % repo.name)


@ays_api.route('/ays/repository/<repository>/simulate', methods=['POST'])
def simulateAction(repository):  # TODO runs are empty
    '''
    simulate the execution of an action
    It is handler for POST /ays/repository/<repository>/simulate
    '''
    if 'action' not in request.args:
        return jsonify(error='No action specified'), 400

    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    action = request.args['action']
    role = request.args.get('role', '')
    instance = request.args.get('instance', '')
    force = j.data.types.bool.fromString(request.args.get('force', False))
    producer_roles = request.args.get('producerroles', '*')
    try:
        run = repo.runGet(role=role, instance=instance, action=action, force=force, producerRoles=producer_roles)
        out = {
            'repository': repository,
            'steps': [],
        }
        for s in run.steps:
            step = {
                'action': s.action,
                'number': s.nr,
                'services_keys': list(s.actions.keys())
            }
            out['steps'].append(step)
        return json.dumps(out), 200, {'Content-Type': 'application/json'}

    except j.exceptions.Input as e:
        return jsonify(error=e.msgpub), 500
    except Exception as e:
        return jsonify(error="Unexpected error: %s" % str(e)), 500


@ays_api.route('/ays/repository/<repository>/execute', methods=['POST'])
def executeAction(repository):
    '''
    Perform an action on a services
    It is handler for POST /ays/repository/<repository>/service/<role>/<instance>/<action>
    '''
    if 'action' not in request.args:
        return jsonify(error='No action specified'), 400

    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    action = request.args['action']
    role = request.args.get('role', '')
    instance = request.args.get('instance', '')
    force = j.data.types.bool.fromString(request.args.get('force', 'False'))
    producer_roles = request.args.get('producerroles', '*')
    async = j.data.types.bool.fromString(request.args.get('async', 'False'))

    rq = repo.runGet(
        action=action,
        instance=instance,
        role=role,
        producerRoles=producer_roles,
        force=force)

    if async:
        msg = "Action %s scheduled" % (action)
        return jsonify(msg=msg), 200

    try:
        rq.execute()
    except Exception as error:
        error_msg = 'Error during execution of action %s: %s' % (action, error)
        logger.error(error_msg)
        return jsonify(error=error_msg), 500

    msg = "Action %s executed successfully" % (action, role, instance, repo.name)
    return jsonify(msg=msg), 200


@ays_api.route('/ays/repository/<repository>/blueprint', methods=['GET'])
def listBlueprints(repository):
    '''
    List all blueprint
    It is handler for GET /ays/repository/<repository>/blueprint
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    include_archived = j.data.types.bool.fromString(request.args.get('archived', 'True'))

    bps = []
    repo._load_blueprints()
    for bp in repo.blueprints:
        bps.append(blueprint_view(bp))
    if include_archived:
        for bp in repo.blueprintsDisabled:
            bps.append(blueprint_view(bp))

    return json.dumps(bps), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/blueprint', methods=['POST'])
def createNewBlueprint(repository):
    '''
    Create a new blueprint
    It is handler for POST /ays/repository/<repository>/blueprint
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    inputs = Blueprint.from_json(json.loads(request.data))
    if not inputs.validate():
        return jsonify(errors=inputs.errors), 400

    repo._load_blueprints()
    new_name = inputs.name.data
    content = inputs.content.data
    names = [bp.name for bp in repo.blueprints]
    if new_name in names:
        return jsonify(error="Blueprint with the name %s' already exists" % new_name), 409

    bp_path = j.sal.fs.joinPaths(repo.path, 'blueprints', new_name)
    try:
        j.sal.fs.writeFile(bp_path, content)
        if new_name not in repo.blueprints:
            repo.blueprints.append(JSBlueprint(repo, path=bp_path))
    except:
        if j.sal.fs.exists(bp_path):
            j.sal.fs.remove(bp_path)
        return jsonify(error="Can't save new blueprint"), 500

    return jsonify(name=new_name, content=content), 201


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>', methods=['PUT'])
def updateBlueprint(blueprint, repository):
    '''
    Update existing blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    inputs = Blueprint.from_json(request.args)
    if not inputs.validate():
        return jsonify(errors=inputs.errors), 400

    repo._load_blueprints()
    name = inputs.name.data
    content = inputs.content.data
    names = [bp.name for bp in repo.blueprints]
    names.extend([bp.name for bp in repo.blueprintsDisabled])

    if name not in names:
        return jsonify(error="blueprint with the name %s not found" % name), 404

    bp_path = j.sal.fs.joinPaths(repo.path, 'blueprints', name)
    bp = repo.blueprintGet(bp_path)
    bp.content = content
    j.sal.fs.writeFile(bp_path, content)

    return json.dumps(blueprint_view(bp)), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>/archive', methods=['PUT'])
def archiveBlueprint(blueprint, repository):
    '''
    Archive existing blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>/archive
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    bp = None
    repo._load_blueprints()
    for item in repo.blueprints:
        if item.name == blueprint:
            bp = item
            break

    if bp is None:
        return jsonify(error="blueprint with the name %s' not found" % blueprint), 404
    bp.disable()

    return jsonify(msg='Blueprint %s archived' % bp.name), 200


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>/restore', methods=['PUT'])
def restoreBlueprint(blueprint, repository):
    '''
    Restore archived blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>/restore
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    bp = None
    repo._load_blueprints()
    for item in repo.blueprintsDisabled:
        if item.name == blueprint:
            bp = item
            break

    if bp is None:
        return jsonify(error="blueprint with the name %s' not found" % blueprint), 404

    bp.enable()

    return jsonify(msg='Blueprint %s restored' % bp.name), 200


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>', methods=['GET'])
def getBlueprint(blueprint, repository):
    '''
    Get a blueprint
    It is handler for GET /ays/repository/<repository>/blueprint/<blueprint>
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    bp = None
    repo._load_blueprints()
    for item in repo.blueprints:
        if item.name == blueprint:
            bp = item
            break

    if bp is None:
        return jsonify(error="No blueprint found with this name '%s'" % blueprint), 404

    return json.dumps(blueprint_view(bp)), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>', methods=['POST'])
def executeBlueprint(blueprint, repository):
    '''
    Execute the blueprint
    It is handler for POST /ays/repository/<repository>/blueprint/<blueprint>
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    bp = None
    repo._load_blueprints()
    for item in repo.blueprints:
        if item.name == blueprint:
            bp = item
            break

    if bp is None:
        return jsonify(error="No blueprint found with this name '%s'" % blueprint), 404

    role = request.args.get('role', '')
    instance = request.args.get('instance', '')

    try:
        repo.blueprintExecute(path=bp.path, role=role, instance=instance)

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

    return jsonify(msg="Blueprint %s initialized" % blueprint)


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>', methods=['DELETE'])
def deleteBlueprint(blueprint, repository):
    '''
    delete blueprint
    It is handler for DELETE /ays/repository/<repository>/blueprint/<blueprint>
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    bp = None
    repo._load_blueprints()
    for item in repo.blueprints:
        if item.name == blueprint:
            bp = item
            break

    if bp is None:
        return jsonify(error="No blueprint found with this name '%s'" % blueprint), 404

    for service in bp.services:
        j.sal.fs.removeDirTree(service.path)

    j.sal.fs.remove(bp.path)
    del repo._blueprints[bp.path]

    return jsonify(), 204


@ays_api.route('/ays/repository/<repository>/service', methods=['GET'])
def listServices(repository):
    '''
    List all services in the repository
    It is handler for GET /ays/repository/<repository>/service
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    repo = j.atyourservice.repoGet(repo.path)
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
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

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
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    svs = repo.services
    s = repo.serviceGet(role=role, instance=name, die=False)
    if s is None:
        return jsonify(error='Service not found'), 404

    service = service_view(s)

    return json.dumps(service), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/service/<role>/<name>/action', methods=['GET'])
def listServiceActions(name, role, repository):
    '''
    Get list of action available on this service
    It is handler for GET /ays/repository/<repository>/service/<role>/<instance>/action
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    s = repo.serviceGet(role=role, instance=name, die=False)
    if s is None:
        return jsonify(error='Service not found'), 404

    actions = sorted(s.model.actionsCode.keys())
    return json.dumps(actions), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/service/<role>/<name>', methods=['DELETE'])
def deleteServiceByName(name, role, repository):
    '''
    uninstall and delete service
    It is handler for DELETE /ays/repository/<repository>/service/<role>/<instance>
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    service = repo.serviceGet(role=role, instance=name, die=False)
    if service is None:
        return jsonify(error='Service role:%s name:%s not found in the repo %s' % (role, name, repository)), 404

    try:
        uninstall = j.data.types.bool.fromString(request.args.get('uninstall', True))

        if uninstall:
            executor = service.executor
            cmd = "cd {path} && ays do uninstall --ask -r {role} -i {instance}".format(path=repo.path, role=service.model.role, instance=service.name)
            rc, out, err = executor.cuisine.core.run(cmd, die=False)
        service.delete()
        if rc > 0 and err != "":
            return jsonify(error="Service is deleted successfully, but uninstallation failed"), 500
    except Exception as e:
        return jsonify(error='unexpected error happened: %s' % str(e)), 500

    return jsonify(), 204


@ays_api.route('/ays/repository/<repository>/actor', methods=['GET'])
def listActors(repository):
    '''
    list all templates
    It is handler for GET /ays/repository/<repository>/actor
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404
    actors = []
    for name, actor in repo.actors.items():
        actors.append(name)

    actors = sorted(actors, key=lambda template: template)

    return json.dumps(actors), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/template', methods=['POST'])
def addTemplateRepo():
    '''
    add a new service template repository
    It is handler for POST /ays/template
    '''

    inputs = TemplateRepo.from_json(request.args)
    if not inputs.validate():
        return jsonify(errors=inputs.errors), 400
    url = inputs.url.data
    branch = inputs.branch.data or "master"

    if url == '':
        return jsonify(error="URL can't be empty"), 400

    if not url.startswith('http'):
        return jsonify(error="URL Format not valid. It should starts with http"), 400

    if url.endswith('.git'):
        url = url[:-len('.git')]

    metadata = j.atyourservice.config['metadata']
    urls = [m['url'] for m in metadata]
    if url in urls:
        return "Repository already exists."

    name = url.split('/')[-1]
    template = {
        'branch': branch,
        'url': url
    }
    j.atyourservice.config['metadata'].append({name, template})
    j.data.serializer.toml.dump('%s/ays/ays.conf' % j.dirs.cfgDir, j.atyourservice.config)

    return jsonify(url=url, branch=branch), 201


@ays_api.route('/ays/repository/<repository>/template', methods=['POST'])
def createNewActor(repository):
    '''
    Create new template
    It is handler for POST /ays/repository/<repository>/template
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    inputs = Template.from_json(request.args)
    if not inputs.validate():
        return jsonify(errors=inputs.errors), 400
    name = inputs.name.data
    actions_py = inputs.actions_py.data
    schema_hrd = inputs.schema_hrd.data

    template_names = list(repo.templates.keys())
    if name in template_names:
        return jsonify(error="template with name '%s' already exists" % name), 409

    templates_dir = j.sal.fs.joinPaths(repo.path, 'actortemplates')
    if not j.sal.fs.exists(templates_dir):
        j.sal.fs.createDir(templates_dir)

    j.sal.fs.createDir(j.sal.fs.joinPaths(templates_dir, name))
    dir_path = j.sal.fs.joinPaths(templates_dir, name)
    if schema_hrd != '' and schema_hrd is not None:
        j.sal.fs.writeFile(j.sal.fs.joinPaths(dir_path, 'schema.hrd'), schema_hrd)
    if actions_py != '' and actions_py is not None:
        j.sal.fs.writeFile(j.sal.fs.joinPaths(dir_path, 'actions.py'), actions_py)

    return jsonify(name=name, action_py=actions_py, schema_hrd=schema_hrd), 201


@ays_api.route('/ays/repository/<repository>/actor/<actor>', methods=['GET'])
def getActor(actor, repository):
    '''
    Get a template
    It is handler for GET /ays/repository/<repository>/actor/<actor>
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    actorsnames = list(repo.actors.keys())
    if actor not in actorsnames:
        return jsonify(error="template not found"), 404

    actor = repo.actors[actor]
    actorv = actor_view(actor)
    return json.dumps(actorv), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/aysrun', methods=['GET'])
def listRuns(repository):
    '''
    list all runs of the repository
    It is handler for GET /ays/repository/<repository>/aysrun
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    try:
        runs = repo.runsList()
        runs = [run_view(run) for run in runs]
        out = {
            'repository': repository,
            'aysruns': runs,
        }
        return json.dumps(out), 200, {'Content-Type': 'application/json'}

    except j.exceptions.Input as e:
        return jsonify(error=e.msgpub), 500
    except Exception as e:
        return jsonify(error="Unexpected error: %s" % str(e)), 500


@ays_api.route('/ays/repository/<repository>/aysrun/<aysrun>', methods=['GET'])
def getRun(aysrun, repository):
    '''
    Get an aysrun
    It is handler for GET /ays/repository/<repository>/aysrun/<aysrun>
    '''
    j.atyourservice.reposDiscover()
    repo = j.atyourservice._repos.get(repository, None)

    if repo is None:
        return jsonify(error='Repository %s not found' % repository), 404

    try:
        aysrun = repo.runGet(aysrun)

    except j.exceptions.Input as e:
        return jsonify(error=e.msg), 404
    except Exception as e:
        return jsonify(error=e.msg), 500

    data = {'model': str(aysrun), 'repr': str(aysrun)}

    return json.dumps(data), 200, {'Content-Type': 'application/json'}
