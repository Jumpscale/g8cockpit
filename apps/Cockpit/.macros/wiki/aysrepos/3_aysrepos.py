

def main(j, args, params, tags, tasklet):
    try:
        repos = j.apps.cockpit.atyourservice.listRepos(ctx=args.requestContext)
        args.doc.applyTemplate({'repos': [r['name'] for r in repos]})
    except Exception as e:
        args.doc.applyTemplate({'error': str(e)})

    params.result = (args.doc, args.doc)
    return params
