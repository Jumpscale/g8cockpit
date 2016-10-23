from JumpScale import j


def service_view(s):
    """
    generate a dict that represent a service from a service object
    """
    producers = {}
    for key, value in s.producers.items():
        producers[key] = [v.__str__() for v in value]
    service = {
        'key': s.model.key,
        'role': s.model.role,
        'name': s.name,
        'instance_hrd': s.model.dataJSON,
        'producers': producers,
        'parent': s.parent.__str__(),
        'path': s.path,
        'repository': s.aysrepo.name,
        'state': s.model.dbobj.state.__str__(),
        'action_py': s.model.actionsCode,
        'model': s.model.__repr__()
    }

    return service


def run_view(run):
    """
    generate a dict that represent a service from a repo object
    """
    # TODO
    return run_view.__repr__()


def template_view(t):
    """
    generate a dict that represent a service from a service object
    """
    template = {
        'name': t.name,
        'schema_hrd': j.sal.fs.fileGetContents("{path}/schema.hrd".format(path=t.path)) if j.sal.fs.exists("{path}/schema.hrd".format(path=t.path)) else None,
        'actions_py': j.sal.fs.fileGetContents("{path}/actions.py".format(path=t.path)) if j.sal.fs.exists("{path}/actions.py".format(path=t.path)) else None,
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
        'path': repo.path,
    }
