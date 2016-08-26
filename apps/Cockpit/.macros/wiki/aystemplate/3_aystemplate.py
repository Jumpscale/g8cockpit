from collections import OrderedDict



def main(j, args, params, tags, tasklet):
    name = args.getTag('aysname')
    ayspath = args.getTag('ayspath') or None

    try:
        template = j.apps.cockpit.atyourservice.getTemplate(repository=ayspath, template=name, ctx=args.requestContext)
        info = {}
        code_bloks = {
            'schema.hrd': template['schema_hrd'],
            'actions.py': template['actions_py'],
            'service.hrd': template['service_hrd']
        }

        instances = j.apps.cockpit.atyourservice.listServices(repo_path=ayspath, role=name, templatename=template['name'], ctx=args.requestContext)
        info = OrderedDict(sorted(info.items()))
        args.doc.applyTemplate({'data': info, 'instances': instances, 'code_bloks': code_bloks, 'template_name': name})
    except Exception as e:
        args.doc.applyTemplate({'error': str(e)})

    params.result = (args.doc, args.doc)
    return params
