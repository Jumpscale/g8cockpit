

def main(j, args, params, tags, tasklet):
    arg_repo = args.getTag('repo')
    arg_runid = args.getTag('runid')

    aysrun = j.apps.system.atyourservice.getRun(runid=arg_runid, repository=arg_repo, ctx=args.requestContext)
    aysrun['model']['time'] = j.data.time.epoch2HRDateTime(aysrun['model']['time'])
    if aysrun['model']['state'] == 'ERROR':
        action = [step['action'] for step in aysrun['model']['steps'] for action in step['actions'] if action['state'] == 'ERROR']
        aysrun['model']['actionkey'] = 'actions.%s.__GUARD__' % action[0] if action else ''
    args.doc.applyTemplate(aysrun)
    params.result = (args.doc, args.doc)
    return params
