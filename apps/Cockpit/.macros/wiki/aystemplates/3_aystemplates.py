

def main(j, args, params, tags, tasklet):
    doc = args.doc
    ayspath = args.getTag('ayspath')
    try:
        templates = j.apps.cockpit.atyourservice.listTemplates(ayspath, ctx=args.requestContext)
        out = {'templates': templates}
        args.doc.applyTemplate(out)
    except Exception as e:
        args.doc.applyTemplate({'error': str(e)})

    params.result = (args.doc, args.doc)
    return params
