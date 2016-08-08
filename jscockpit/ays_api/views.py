from JumpScale import j


def service_view(s):
    """
    generate a dict that represent a service from a service object
    """
    service = {
        'key': s.key,
        'role': s.role,
        'name': s.recipe.name,
        'instance': s.instance,
        'instance_hrd': s.hrd.getHRDAsDict()if s.hrd is not None else None,
        'producers': [],
        'parent': None,
        'path': s.path,
        'repository': s.aysrepo.name,
        'state': {},
        'action_py': None,
    }

    state_path = j.sal.fs.joinPaths(s.path, 'state.yaml')
    if j.sal.fs.exists(state_path):
        state_json = j.data.serializer.yaml.load(state_path)
        service['state'] = state_json

    action_path = j.sal.fs.joinPaths(s.path, 'actions.py')
    if j.sal.fs.exists(action_path):
        service['action.py'] = j.sal.fs.fileGetContents(action_path)

    if s.parent is not None:
        service['parent'] = service_view(s.parent)

    for role, prods in s.producers.items():
        for prod in prods:
            service['producers'].append(service_view(prod))

    return service


def template_view(t):
    """
    generate a dict that represent a service from a service object
    """
    template = {
        'name': t.name,
        'service_hrd': t.hrd.getHRDAsDict() if t.hrd else None,
        'schema_hrd': j.sal.fs.fileGetContents(t.path_hrd_schema) if j.sal.fs.exists(t.path_hrd_schema) else None,
        'actions_py': j.sal.fs.fileGetContents(t.path_actions) if j.sal.fs.exists(t.path_actions) else None,
    }
    return template


def blueprint_view(bp):
    return {
        'path': bp.path,
        'name': bp.name,
        'content': bp.content,
        'hash': bp.hash,
        'archived': not bp.active,
    }


def repository_view(repo):
    return {
        'name': repo.name,
        'path': repo.basepath,
    }
