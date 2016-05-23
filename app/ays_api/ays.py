from flask import Blueprint as fBlueprint, jsonify, request, json, Response
from JumpScale import j


from .Repository import Repository

# from BlueprintPostReqBody import BlueprintPostReqBody
from .Blueprint import Blueprint

from .Template import Template


ays_api = fBlueprint('ays_api', __name__)


@ays_api.route('/ays/repository', methods=['GET'])
def ays_repository_get():
    '''
    list all repositorys
    It is handler for GET /ays/repository
    '''
    repos = []
    for path in j.atyourservice.findAYSRepos():
        repos.append({'name': j.sal.fs.getBaseName(path), 'path': path})
    return json.dumps(repos), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository', methods=['POST'])
def ays_repository_post():
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

    path = j.sal.fs.joinPaths(j.dirs.codeDir, name)
    j.atyourservice.createAYSRepo(path)
    return jsonify(name=name, path=path), 201


@ays_api.route('/ays/repository/<repository>', methods=['GET'])
def ays_repository_byRepository_get(repository):
    '''
    Get information of a repository
    It is handler for GET /ays/repository/<repository>
    '''
    if repository not in j.atyourservice.repos:
        return jsonify(error='Repository not found with name %s' % repository), 404

    repo = j.atyourservice.repos[repository]
    return jsonify(name=repo.name, path=repo.basepath)


@ays_api.route('/ays/repository/<repository>', methods=['DELETE'])
def ays_repository_byRepository_delete(repository):
    '''
    Delete a repository
    It is handler for DELETE /ays/repository/<repository>
    '''
    if repository not in j.atyourservice.repos:
        return jsonify(error='Repository not found with name %s' % repository), 404

    repo = j.atyourservice.repos[repository]
    repo.uninstall()
    del j.atyourservice.repos[repository]
    j.sal.fs.removeDirTree(repo.basepath)
    return '', 204


@ays_api.route('/ays/repository/<repository>/blueprint', methods=['GET'])
def ays_repository_byRepository_blueprint_get(repository):
    '''
    List all blueprint
    It is handler for GET /ays/repository/<repository>/blueprint
    '''
    if repository not in j.atyourservice.repos:
        return jsonify(error='Repository not found with name %s' % repository), 404

    repo = j.atyourservice.repos[repository]
    bps = []
    for bp in repo.blueprints:
        bps.append({
            'name': j.sal.fs.getBaseName(bp.path),
            'content': bp.content
        })
    return json.dumps(bps), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/blueprint', methods=['POST'])
def ays_repository_byRepository_blueprint_post(repository):
    '''
    Create a new blueprint
    It is handler for POST /ays/repository/<repository>/blueprint
    '''
    if repository not in j.atyourservice.repos:
        return jsonify(error='Repository not found with name %s' % repository), 404

    repo = j.atyourservice.repos[repository]

    inputs = Blueprint.from_json(request.get_json())
    if not inputs.validate():
        return jsonify(errors=inputs.errors), 400

    new_name = inputs.name.data
    content = inputs.content.data

    names = [bp.name for bp in repo.blueprints]
    if new_name in names:
        return jsonify(error="blueprint with the name %s' already exsits" % new_name), 409

    bp_path = j.sal.fs.joinPaths(repo.basepath, 'blueprints', inputs.name.data)
    j.sal.fs.writeFile(bp_path, content)

    return jsonify(name=new_name, content=content), 201


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>', methods=['GET'])
def ays_repository_byRepository_blueprint_byBlueprint_get(blueprint, repository):
    '''
    Get a blueprint
    It is handler for GET /ays/repository/<repository>/blueprint/<blueprint>
    '''
    if repository not in j.atyourservice.repos:
        return jsonify(error='Repository not found with name %s' % repository), 404

    repo = j.atyourservice.repos[repository]

    bp = None
    for item in repo.blueprints:
        if item.name == blueprint:
            bp = item
            break

    if bp is None:
        return jsonify(error="No blueprint found with this name '%s'" % blueprint), 404

    return jsonify(name=bp.name, content=bp.content)


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>', methods=['POST'])
def ays_repository_byRepository_blueprint_byBlueprint_post(blueprint, repository):
    '''
    Execute the blueprint
    It is handler for POST /ays/repository/<repository>/blueprint/<blueprint>
    '''
    if repository not in j.atyourservice.repos:
        return jsonify(error='Repository not found with name %s' % repository), 404

    repo = j.atyourservice.repos[repository]

    bp = None
    for item in repo.blueprints:
        if item.name == blueprint:
            bp = item
            break

    if bp is None:
        return jsonify(error="No blueprint found with this name '%s'" % blueprint), 404

    try:
        bp.load()
        repo.init()
        run = repo.getRun(action="install")
        run.execute()
    except Exception as e:
        return jsonify(error="Error during execution of the blueprint:\n %s" % str(e)), 500

    return jsonify(msg="blueprint %s initialized" % repo.name)


@ays_api.route('/ays/repository/<repository>/blueprint/<blueprint>', methods=['DELETE'])
def ays_repository_byRepository_blueprint_byBlueprint_delete(blueprint, repository):
    '''
    delete blueprint
    It is handler for DELETE /ays/repository/<repository>/blueprint/<blueprint>
    '''
    if repository not in j.atyourservice.repos:
        return jsonify(error='Repository not found with name %s' % repository), 404

    repo = j.atyourservice.repos[repository]

    bp = None
    for item in repo.blueprints:
        if item.name == blueprint:
            bp = item
            break

    if bp is None:
        return jsonify(error="No blueprint found with this name '%s'" % blueprint), 404

    for service in bp.services:
        repo.uninstall(role=service.role, instance=service.instance)
    for service in bp.services:
        j.sal.fs.removeDirTree(service.path)

    j.sal.fs.remove(bp.path)
    repo.blueprints.remove(bp)

    return jsonify(), 204


@ays_api.route('/ays/repository/<repository>/service', methods=['GET'])
def ays_repository_byRepository_service_get(repository):
    '''
    List all services in the repository
    It is handler for GET /ays/repository/<repository>/service
    '''
    if repository not in j.atyourservice.repos:
        return jsonify(error='Repository not found with name %s' % repository), 404

    repo = j.atyourservice.repos[repository]
    services = []
    for s in repo.services.values():
        service = {
            'role': s.role,
            'name': s.recipe.name,
            'instance': s.instance
        }
        services.append(service)

    return json.dumps(services), 200, {'Content-Type': 'application/json'}

# @ays_api.route('/ays/repository/<repository>/service/<role>', methods=['GET'])
# def ays_repository_byRepository_service_byRole_get(role, repository):
#     '''
#     List all services of role 'role' in the repository
#     It is handler for GET /ays/repository/<repository>/service/<role>
#     '''
#
#     return jsonify()


@ays_api.route('/ays/repository/<repository>/service/<role>/action/<action>', methods=['POST'])
def ays_repository_byRepository_service_byRole_action_byAction_post(action, role, repository):
    '''
    Perform an action on all service with the role 'role'
    It is handler for POST /ays/repository/<repository>/service/<role>/action/<action>
    '''

    return jsonify()


@ays_api.route('/ays/repository/<repository>/service/<role>/<instance>', methods=['GET'])
def ays_repository_byRepository_service_byRole_byInstance_get(instance, role, repository):
    '''
    Get a service instance
    It is handler for GET /ays/repository/<repository>/service/<role>/<instance>
    '''
    if repository not in j.atyourservice.repos:
        return jsonify(error='Repository not found with name %s' % repository), 404

    repo = j.atyourservice.repos[repository]
    s = repo.getService(role=role, instance=instance, die=False)
    if s is None:
        return jsonify(error='Service not found'), 404

    service = {
        'role': s.role,
        'name': s.recipe.name,
        'instance': s.instance
    }
    paths = {
        'action.py': j.sal.fs.joinPaths(s.path, 'actions.py'),
        'state': j.sal.fs.joinPaths(s.path, 'state.yaml'),
        'instance.hrd': j.sal.fs.joinPaths(s.path, 'instance.hrd')
    }
    for k, p in paths.items():
        if j.sal.fs.exists(p):
            service[k] = j.sal.fs.fileGetContents(p)

    return json.dumps(service), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/service/<role>/<instance>/action', methods=['GET'])
def ays_repository_byRepository_service_byRole_byInstance_action_get(instance, role, repository):
    '''
    Get list of action available on this service
    It is handler for GET /ays/repository/<repository>/service/<role>/<instance>/action
    '''
    if repository not in j.atyourservice.repos:
        return jsonify(error='Repository not found with name %s' % repository), 404

    repo = j.atyourservice.repos[repository]
    s = repo.getService(role=role, instance=instance, die=False)
    if s is None:
        return jsonify(error='Service not found'), 404

    actions = list(s.action_methods.keys())
    actions.sort()
    return json.dumps(actions), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/service/<role>/<instance>/<action>', methods=['POST'])
def ays_repository_byRepository_service_byRole_byInstance_byAction_post(action, instance, role, repository):
    '''
    Perform an action on a services
    It is handler for POST /ays/repository/<repository>/service/<role>/<instance>/<action>
    '''

    return jsonify()


@ays_api.route('/ays/repository/<repository>/template', methods=['GET'])
def ays_repository_byRepository_template_get(repository):
    '''
    list all templates
    It is handler for GET /ays/repository/<repository>/template
    '''
    if repository not in j.atyourservice.repos:
        return jsonify(error='Repository not found with name %s' % repository), 404

    repo = j.atyourservice.repos[repository]

    templates = list(repo.templates.keys())
    templates.sort()
    return json.dumps(templates), 200, {'Content-Type': 'application/json'}


@ays_api.route('/ays/repository/<repository>/template', methods=['POST'])
def ays_repository_byRepository_template_post(repository):
    '''
    Create new template
    It is handler for POST /ays/repository/<repository>/template
    '''
    if repository not in j.atyourservice.repos:
        return jsonify(error='Repository not found with name %s' % repository), 404

    repo = j.atyourservice.repos[repository]

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
def ays_repository_byRepository_template_byTemplate_get(template, repository):
    '''
    Get a template
    It is handler for GET /ays/repository/<repository>/template/<template>
    '''
    if repository not in j.atyourservice.repos:
        return jsonify(error='Repository not found with name %s' % repository), 404

    repo = j.atyourservice.repos[repository]

    template_names = list(repo.templates.keys())
    if template not in template_names:
        return jsonify(error="template not found"), 404

    tmpl = repo.templates[template]
    out = {'name': tmpl.name}

    path = j.sal.fs.joinPaths(tmpl.path, 'schema.hrd')
    if j.sal.fs.exists(path):
        out['schema_hrd'] = j.sal.fs.fileGetContents(path)
    path = j.sal.fs.joinPaths(tmpl.path, 'actions.py')
    if j.sal.fs.exists(path):
        out['action_py'] = j.sal.fs.fileGetContents(path)

    return json.dumps(out), 200, {'Content-Type': 'application/json'}
