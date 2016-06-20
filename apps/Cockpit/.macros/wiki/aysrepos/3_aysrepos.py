

def main(j, args, params, tags, tasklet):
    repos = j.apps.system.atyourservice.listRepos(ctx=args.requestContext)
    args.doc.applyTemplate({'repos': [r['name'] for r in repos]})
    params.result = (args.doc, args.doc)
    return params
