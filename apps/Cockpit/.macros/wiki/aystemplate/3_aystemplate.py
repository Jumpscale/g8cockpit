from collections import OrderedDict


def main(j, args, params, tags, tasklet):
    name = args.getTag('aysname')
    ayspath = args.getTag('ayspath') or None

    template = j.apps.system.atyourservice.getTemplate(repository=ayspath, template=name, ctx=args.requestContext)
    info = {}
    code_bloks = {
        'schema.hrd': template['schema.hrd'],
        'actions.py': template['actions.py'],
        'service.hrd': template['service.hrd']
    }

    instances = []
    for ayspath, services in j.apps.system.atyourservice.listServices(repo_path=ayspath, role=name).items():
        for service in services.values():
            instances.append('[%s|cockpit/Instance?shortkey=%s&ayspath=%s]' % (service['instance'], service['key'], ayspath))

    info = OrderedDict(sorted(info.items()))
    args.doc.applyTemplate({'data': info, 'instances': instances, 'code_bloks': code_bloks})
    params.result = (args.doc, args.doc)
    return params
