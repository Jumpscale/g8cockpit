

def main(j, args, params, tags, tasklet):
    arg_repo = args.getTag('repo')
    arg_runid = args.getTag('runid')

    aysrun = j.apps.system.atyourservice.getRun(runid=arg_runid, repository=arg_repo, ctx=args.requestContext)
    aysrun['model']['time'] = j.data.time.epoch2HRDateTime(aysrun['model']['time'])
    args.doc.applyTemplate(aysrun)
    params.result = (args.doc, args.doc)
    return params
