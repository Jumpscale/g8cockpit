from JumpScale.portal.portal import exceptions

def main(j, args, params, tags, tasklet):
    doc = args.doc
    ayspath = args.getTag('ayspath')
    try:
        templates = j.apps.cockpit.atyourservice.listTemplates(ayspath, ctx=args.requestContext)
        out = {'templates': templates}
        args.doc.applyTemplate(out)
    except exceptions.BaseError as e:
        args.doc.applyTemplate({'error': e.msg})

    params.result = (args.doc, args.doc)
    return params
