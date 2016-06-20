from collections import OrderedDict


def main(j, args, params, tags, tasklet):
    query_params = args.requestContext.params
    repo = query_params.get('repo', None)
    action = query_params.get('action', None)
    role = query_params.get('role', '')
    instance = query_params.get('instance', '')
    force = query_params.get('force', '')

    if not action or not repo:
        params.result = ('', args.doc)
        return params
    actor = j.apps.actorsloader.getActor("system", "atyourservice")

    out = ["h3. Result of simulation for action '%s'" % action]
    try:
        run = actor.simulate(repository=repo, action=action, role=role, instance=instance, force=force, ctx=args.requestContext)
        if len(run['steps']) <= 0:
            out.append("All done, nothing more to do.")
        for step in run['steps']:
            out.append("h4. step:%s" % step['number'])
            for key in step['services_keys']:
                out.append('* %s - %s' % (key, step['action']))
                out.append("")
    except Exception as e:
        out.append(str(e))

    params.result = ('\n'.join(out), args.doc)
    return params
