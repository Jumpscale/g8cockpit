

def main(j, args, params, tags, tasklet):
    arg_repo = args.getTag('repo')
    repos = j.apps.cockpit.atyourservice.listRepos(ctx=args.requestContext)
    repo = None
    for r in repos:
        if arg_repo == r['name']:
            repo = r
            break

    if repo is not None:
        repo['path'] = repo['path'].replace(j.dirs.codeDir, '$codedir')
        args.doc.applyTemplate({'repo': repo})
        params.result = (args.doc, args.doc)
    else:
        params.result = ("Cant find repository %s" % repo, args.doc)
    return params
