from collections import OrderedDict


def main(j, args, params, tags, tasklet):
    shortkey = args.getTag('shortkey')
    ayspath = args.getTag('ayspath')

    service = j.apps.system.atyourservice.listServices(repo_path=ayspath)[ayspath][shortkey]
    obj = service.hrd.getHRDAsDict()
    obj.pop('service.name', None)

    hidden = ['key.priv', 'password', 'passwd', 'pwd']
    for key in list(set(obj.keys()) & set(hidden)):
        obj[key] = '**VALUE HIDDEN**'

    for key, value in service.producers.items():
        producer = 'producer.%s' % key
        producer_name = value[0]
        obj[producer] = ('[%s|cockpit/AYSInstance?shortkey=%s&ayspath=%s]' % (producer_name.instance, producer_name, ayspath))

    if service.parent:
        parent = service.parent
        service.parents.remove(parent)
        obj['parent'] = ('[%s|cockpit/AYSInstance?shortkey=%s&ayspath=%s]' % (parent.instance, parent, ayspath))

    parents = service.parents
    if parents:
        obj['parents'] = list()
        for parent in parents:
            obj['parents'].append(('[%s|cockpit/AYSInstance?shortkey=%s&ayspath=%s]' % (parent.instance, parent, ayspath)))

        obj['parents'] = ', '.join(obj['parents'])

    link_to_template = ('[%s|cockpit/AYSTemplate?ayspath=%s&aysname=%s]' % (service.role,
                                                                              service.aysrepo.name, service.role))
    obj = OrderedDict(sorted(obj.items()))

    # we prepend service path with '$codedir' to make it work in the explorer.
    # because of this line : https://github.com/Jumpscale/jumpscale_portal8/blob/master/apps/portalbase/macros/page/explorer/1_main.py#L25
    path = service.path.replace(j.dirs.codeDir, '$codedir')
    args.doc.applyTemplate({'data': obj, 'type': link_to_template, 'instance': service.instance, 'role': service.role, 'state': service.state, 'path': path})
    params.result = (args.doc, args.doc)
    return params
