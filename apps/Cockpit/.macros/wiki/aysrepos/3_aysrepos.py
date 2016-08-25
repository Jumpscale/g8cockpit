from JumpScale.portal.portal import exceptions

def main(j, args, params, tags, tasklet):
    try:
        repos = j.apps.cockpit.atyourservice.listRepos(ctx=args.requestContext)
        args.doc.applyTemplate({'repos': [r['name'] for r in repos]})
    except exceptions.BaseError as e:
        args.doc.applyTemplate({'error': e.msg})

    params.result = (args.doc, args.doc)
    return params
