from collections import OrderedDict
from JumpScale.portal.portal import exceptions


def main(j, args, params, tags, tasklet):
    shortkey = args.getTag('shortkey')
    ayspath = args.getTag('ayspath')

    actor = j.apps.actorsloader.getActor("cockpit", "atyourservice")
    domain, name, instance, role = j.atyourservice._parseKey(shortkey)
    try:
        service = actor.getService(repository=ayspath, role=role, instance=instance, ctx=args.requestContext)
        state = state = service.pop('state', {'state': {}})
        hrd = service.pop('instance_hrd')

        hidden = ['key.priv', 'password', 'passwd', 'pwd', 'oauth.jwt_key']
        for key in list(set(hrd.keys()) & set(hidden)):
            hrd[key] = "*VALUE HIDDEN*"

        producers = {}
        for producer in service.pop('producers'):
            role = producer['role']
            if role not in producers:
                producers[role] = []
            producer['link'] = '[{instance}|/cockpit/Instance?shortkey={key}&ayspath={path}]'.format(
                instance=producer['instance'], key=producer['key'], path=ayspath)
            producers[role].append(producer)

        parent = {}
        if service['parent'] is not None:
            parent = service.pop('parent')
            parent['link'] = '[{instance}|/cockpit/Instance?shortkey={key}&ayspath={path}]'.format(
                instance=parent['instance'], key=parent['key'], path=ayspath)

        link_to_template = ('[%s|cockpit/Template?ayspath=%s&aysname=%s]' % (service['name'],
                                                                             ayspath, service['role']))

        # we prepend service path with '$codedir' to make it work in the explorer.
        # because of this line : https://github.com/Jumpscale/jumpscale_portal8/blob/master/apps/portalbase/macros/page/explorer/1_main.py#L25
        for action in state['state'].keys():
            if action in state['recurring']:
                obj = state['recurring'][action]
                state['recurring'][action] = {
                    'period': obj[0],
                    'last': obj[1],
                }
            else:
                state['recurring'][action] = {
                    'period': "not recurrent",
                    'last': "never",
                }
        args.doc.applyTemplate({
            'service': service,
            'type': link_to_template,
            'instance': service['instance'],
            'role': service['role'],
            'state': state,
            'producers': OrderedDict(sorted(producers.items())),
            'hrd': OrderedDict(sorted(hrd.items())),
            'parent': parent,
        })

    except exceptions.BaseError as e:
        args.doc.applyTemplate({'error': e.msg})

    params.result = (args.doc, args.doc)
    return params
