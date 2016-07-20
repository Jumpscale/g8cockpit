

def main(j, args, params, tags, tasklet):
    arg_repo = args.getTag('repo')
    arg_hrd_hash = args.getTag('hrd')
    arg_source_hash = args.getTag('source')

    hrd = j.apps.cockpit.atyourservice.getHRD(hash=arg_hrd_hash, repository=arg_repo, ctx=args.requestContext)
    source = j.apps.cockpit.atyourservice.getSource(hash=arg_source_hash, repository=arg_repo, ctx=args.requestContext)

    args.doc.applyTemplate({'hrd': hrd, 'source': source})
    params.result = (args.doc, args.doc)

    return params
