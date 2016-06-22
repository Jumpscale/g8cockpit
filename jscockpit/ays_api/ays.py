from flask import Blueprint as fBlueprint, jsonify, request, json, Response, current_app
from JumpScale import j
from JumpScale.baselib.atyourservice.Blueprint import Blueprint as JSBlueprint
from .views import service_view, template_view, blueprint_view, repository_view

from .Repository import Repository
from .Blueprint import Blueprint
from .Template import Template


ays_api = fBlueprint('ays_api', __name__)
logger = j.logger.get('j.app.cockpit.api')


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
    repos = []
    for repo in j.atyourservice.repos.values():
        repos.append(repository_view(repo))

    return json.dumps(repos), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository', methods=['POST'])
def createNewRepository():
    '''
    create a new repository
    It is handler for POST /ays/repository
    '''
    inputs = Repository.from_json(request.get_json())
    if not inputs.validate():
        return jsonify(errors=inputs.errors), 400

    name = inputs.name.data
    if name in j.atyourservice.repos:
        return jsonify(error='repo with this name already exsits'), 409

    path = j.sal.fs.joinPaths(j.dirs.codeDir, "cockpit", name)
    j.atyourservice.createAYSRepo(path)
    return jsonify(name=name, path=path), 201


@ays_api.route('/ays/repository/<repository>', methods=['GET'])
def getRepository(repository):
    '''
    Get information of a repository
    It is handler for GET /ays/repository/<repository>
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404
    return jsonify(name=repo.name, path=repo.basepath)


@ays_api.route('/ays/repository/<repository>', methods=['DELETE'])
def deleteRepository(repository):
    '''
    Delete a repository
    It is handler for DELETE /ays/repository/<repository>
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404
    repo.uninstall()
    del j.atyourservice.repos[repository]
    j.sal.fs.removeDirTree(repo.basepath)
    return '', 204

@ays_api.route('/ays/repository/<repository>/init', methods=['POST'])
def initRepository(repository):
    '''
    Init a repository
    It is handler for POST /ays/repository/<repository>/init
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404
    role = request.args.get('role', '')
    instance = request.args.get('instance', '')

    try:
        repo.init(role=role, instance=instance)
    except Exception as e:
        error_msg = "Error during execution of init on repository %s:\n %s" % (repo.name, str(e))
        logger.error(error_msg)
        return jsonify(error=error_msg), 500

    return jsonify(msg="blueprint %s initialized" % repo.name)

@ays_api.route('/ays/repository/<repository>/simulate', methods=['POST'])
def simulateAction(repository):
    '''
    simulate the execution of an action
    It is handler for POST /ays/repository/<repository>/simulate
    '''
    if 'action' not in request.args:
        return jsonify(error='No action specified'), 400

    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404
    action = request.args['action']
    role = request.args.get('role', '')
    instance = request.args.get('instance', '')
    force = j.data.types.bool.fromString(request.args.get('force', False))
    producer_roles = request.args.get('producerroles', '*')
    try:
        run = repo.getRun(role=role, instance=instance, action=action, force=force, producerRoles=producer_roles)
        out = {
            'repository': repository,
            'steps': [],
        }
        for s in run.steps:
            step = {
                'action': s.action,
                'number': s.nr,
                'services_keys': list(s.serviceKeys.keys())
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

    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404
    action = request.args['action']
    role = request.args.get('role', '')
    instance = request.args.get('instance', '')
    force = j.data.types.bool.fromString(request.args.get('force', 'False'))
    producer_roles = request.args.get('producerroles', '*')
    async = j.data.types.bool.fromString(request.args.get('async', 'False'))

    rq = current_app.ays_bot.schedule_action(action, repo.name, role=role, instance=instance, force=force, notify=False, chat_id=None)

    if async:
        msg = "Action %s scheduled" % (action)
        return jsonify(msg=msg), 200

    result = rq.get()
    if 'error' in result:
        error_msg = 'Error execution of action %s of service %s!%s from repo `%s`: %s' % (action, role, instance, repo.name, result['error'])
        logger.error(error_msg)
        return jsonify(error=error_msg), 500

    msg = "Action %s on service %s instance %s in repo %s exectued without error" % (action, role, instance, repo.name)
    return jsonify(msg=msg), 200


@ays_api.route('/ays/repository/<repository>/blueprint', methods=['GET'])
def listBlueprints(repository):
    '''
    List all blueprint
    It is handler for GET /ays/repository/<repository>/blueprint
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404

    include_archived = j.data.types.bool.fromString(request.args.get('archived', 'True'))

    bps = []
    for bp in repo.blueprints:
        bps.append(blueprint_view(bp))
    if include_archived:
        for bp in repo.blueprints_archive:
            bps.append(blueprint_view(bp))

    return json.dumps(bps), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/blueprint', methods=['POST'])
def createNewBlueprint(repository):
    '''
    Create a new blueprint
    It is handler for POST /ays/repository/<repository>/blueprint
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404

    inputs = Blueprint.from_json(request.get_json())
    if not inputs.validate():
        return jsonify(errors=inputs.errors), 400

    new_name = inputs.name.data
    content = inputs.content.data

    names = [bp.name for bp in repo.blueprints]
    if new_name in names:
        return jsonify(error="blueprint with the name %s' already exsits" % new_name), 409

    bp_path = j.sal.fs.joinPaths(repo.basepath, 'blueprints', new_name)
    try:
        j.sal.fs.writeFile(bp_path, content)
        if bp_path not in repo._blueprints:
            repo._blueprints[bp_path] = JSBlueprint(repo, path=bp_path)
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
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404

    inputs = Blueprint.from_json(request.get_json())
    if not inputs.validate():
        return jsonify(errors=inputs.errors), 400

    name = inputs.name.data
    content = inputs.content.data
    names = [bp.name for bp in repo.blueprints]
    names.extend([bp.name for bp in repo.blueprints_archive])
    if name not in names:
        return jsonify(error="blueprint with the name %s' not found" % name), 404

    bp_path = j.sal.fs.joinPaths(repo.basepath, 'blueprints', name)
    bp = repo.getBlueprint(bp_path)
    bp.content = content
    j.sal.fs.writeFile(bp_path, content)

    return json.dumps(blueprint_view(bp)), 200, {'Content-Type': 'application/json'}

@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>/archive', methods=['PUT'])
def archiveBlueprint(blueprint, repository):
    '''
    Archive existing blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>/archive
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404

    bp = None
    for item in repo.blueprints:
        if item.name == blueprint:
            bp = item
            break

    if bp is None:
        return jsonify(error="blueprint with the name %s' not found" % blueprint), 404

    repo.archive_blueprint(bp)

    return jsonify(msg='Blueprint %s archived' % bp.name), 200

@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>/restore', methods=['PUT'])
def restoreBlueprint(blueprint, repository):
    '''
    Restore archived blueprint
    It is handler for PUT /ays/repository/<repository>/blueprint/<blueprint>/restore
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404

    bp = None
    for item in repo.blueprints_archive:
        if item.name == blueprint:
            bp = item
            break

    if bp is None:
        return jsonify(error="blueprint with the name %s' not found" % blueprint), 404

    repo.restore_blueprint(bp)

    return jsonify(msg='Blueprint %s restored' % bp.name), 200


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>', methods=['GET'])
def getBlueprint(blueprint, repository):
    '''
    Get a blueprint
    It is handler for GET /ays/repository/<repository>/blueprint/<blueprint>
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404

    bp = None
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
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404
    bp = None
    for item in repo.blueprints:
        if item.name == blueprint:
            bp = item
            break

    if bp is None:
        return jsonify(error="No blueprint found with this name '%s'" % blueprint), 404

    role = request.args.get('role', '')
    instance = request.args.get('instance', '')

    try:
        repo.execute_blueprint(content=bp.content, role=role, instance=instance)

        # notify bot new services have been created
        # TODO: unify event for telegram and REST
        evt = j.data.models.cockpit_event.Telegram()
        evt.io = 'input'
        evt.action = 'bp.create'
        evt.args = {
            'path': bp.path,
            'content': bp.content,
        }
        j.core.db.publish('telegram', evt.to_json())

    except Exception as e:
        error_msg = "Error during execution of the blueprint:\n %s" % str(e)
        logger.error(error_msg)
        return jsonify(error=error_msg), 500

    return jsonify(msg="blueprint %s initialized" % repo.name)


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>', methods=['DELETE'])
def deleteBlueprint(blueprint, repository):
    '''
    delete blueprint
    It is handler for DELETE /ays/repository/<repository>/blueprint/<blueprint>
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404

    bp = None
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
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404
    services = []
    for s in repo.services.values():
        services.append(service_view(s))

    services = sorted(services, key=lambda service: service['role'])

    return json.dumps(services), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/service/<role>', methods=['GET'])
def listServicesByRole(role, repository):
    '''
    List all services of role 'role' in the repository
    It is handler for GET /ays/repository/<repository>/service/<role>
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404
    services = []
    for s in repo.findServices(role=role):
        services.append(service_view(s))

    services = sorted(services, key=lambda service: service['role'])

    return json.dumps(services), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/service/<role>/<instance>', methods=['GET'])
def getServiceByInstance(instance, role, repository):
    '''
    Get a service instance
    It is handler for GET /ays/repository/<repository>/service/<role>/<instance>
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404
    s = repo.getService(role=role, instance=instance, die=False)
    if s is None:
        return jsonify(error='Service not found'), 404

    service = service_view(s)

    return json.dumps(service), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/service/<role>/<instance>/action', methods=['GET'])
def listServiceActions(instance, role, repository):
    '''
    Get list of action available on this service
    It is handler for GET /ays/repository/<repository>/service/<role>/<instance>/action
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404
    s = repo.getService(role=role, instance=instance, die=False)
    if s is None:
        return jsonify(error='Service not found'), 404

    actions = list(s.action_methods.keys())
    actions.sort()
    return json.dumps(actions), 200, {'Content-Type': 'application/json'}

@ays_api.route('/ays/repository/<repository>/service/<role>/<instance>', methods=['DELETE'])
def deleteServiceByInstance(instance, role, repository):
    '''
    uninstall and delete service
    It is handler for DELETE /ays/repository/<repository>/service/<role>/<instance>
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404
    service = repo.getService(role=role, instance=instance, die=False)
    if service is None:
        return jsonify(error='Service role:%s instance:%s not found in the repo %s' % (role, instance, repository)), 404

    try:
        scope = request.args.getlist('scope')
        producerRoles = ','.join(scope) if scope else '*'
        repo.uninstall(role=role, instance=instance, producerRoles=producerRoles)
        del repo.services[service.key]
        j.sal.fs.removeDirTree(service.path)
    except Exception as e:
        return jsonify(error='unexpected error happened: %s' % str(e)), 500

    return jsonify(), 204


@ays_api.route('/ays/repository/<repository>/template', methods=['GET'])
def listTemplates(repository):
    '''
    list all templates
    It is handler for GET /ays/repository/<repository>/template
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404
    templates = []
    for name, tmpl in repo.templates.items():
        templates.append(template_view(tmpl))

    templates = sorted(templates, key=lambda template: template['name'])

    return json.dumps(templates), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/template', methods=['POST'])
def createNewTemplate(repository):
    '''
    Create new template
    It is handler for POST /ays/repository/<repository>/template
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404

    inputs = Template.from_json(request.get_json())
    if not inputs.validate():
        return jsonify(errors=inputs.errors), 400

    name = inputs.name.data
    actions_py = inputs.actions_py.data
    schema_hrd = inputs.schema_hrd.data

    template_names = list(repo.templates.keys())
    if name in template_names:
        return jsonify(error="template with name '%s' already exists" % name), 409

    templates_dir = j.sal.fs.joinPaths(repo.basepath, 'servicetemplates')
    if not j.sal.fs.exists(templates_dir):
        j.sal.createDir(templates_dir)

    j.sal.fs.createDir(j.sal.fs.joinPaths(templates_dir, name))
    dir_path = j.sal.fs.joinPaths(templates_dir, name)
    if schema_hrd != '' and schema_hrd is not None:
        j.sal.fs.writeFile(j.sal.fs.joinPaths(dir_path, 'schema.hrd'), schema_hrd)
    if actions_py != '' and actions_py is not None:
        j.sal.fs.writeFile(j.sal.fs.joinPaths(dir_path, 'actions.py'), actions_py)

    return jsonify(name=name, action_py=actions_py, schema_hrd=schema_hrd), 201


@ays_api.route('/ays/repository/<repository>/template/<template>', methods=['GET'])
def getTemplate(template, repository):
    '''
    Get a template
    It is handler for GET /ays/repository/<repository>/template/<template>
    '''
    repo = j.atyourservice.repos.get(repository, None)
    if repo is None:
        return jsonify(error='Repository not found with name %s' % repository), 404

    template_names = list(repo.templates.keys())
    if template not in template_names:
        return jsonify(error="template not found"), 404

    tmpl = repo.templates[template]
    template = template_view(tmpl)

    return json.dumps(template), 200, {'Content-Type': 'application/json'}
