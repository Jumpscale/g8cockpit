from collections import OrderedDict
from JumpScale.portal.portal import exceptions


def main(j, args, params, tags, tasklet):
    import jinja2
    params.result = page = args.page
    doc = args.doc
    arg_repo = args.getTag('repo')
    klass = 'jstimestamp'

    data = {}
    try:
        for repo_path, runs in j.apps.cockpit.atyourservice.listRuns(repository=arg_repo, ctx=args.requestContext).items():
            if repo_path not in data:
                data[repo_path] = []

            aysruns = []
            for key, value in runs['aysruns'].items():
                runat, state = value.split('|')
                runid = int(key)
                aysrun = {'id': runid,
                          'state': state,
                          'sortkey': '%05d' % runid,
                          'runat': runat}
                aysruns.append(aysrun)

            data[repo_path].extend(sorted(aysruns, key=lambda x: x['id']))

        args.doc.applyTemplate({'data': data})
    except exceptions.BaseError as e:
        args.doc.applyTemplate({'error': e.msg})

    params.result = (args.doc, args.doc)
    return params
