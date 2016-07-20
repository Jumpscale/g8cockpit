from collections import OrderedDict

def main(j, args, params, tags, tasklet):
    doc = args.doc
    arg_repo = args.getTag('repo')
    out = list()

    # this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n")
    for repo_path, runs in j.apps.cockpit.atyourservice.listRuns(repository=arg_repo, ctx=args.requestContext).items():
        out.append('h5. AYSRepo: %s' % repo_path)
        out.append('|| Run ID || Ran At || State ||')

        runs = OrderedDict(sorted(runs['aysruns'].items()))
        for runid, run_info in runs.items():
            line = ['|[%s|cockpit/Run?repo=%s&runid=%s]' % (runid, repo_path, runid)]
            time, state = run_info.split('|')
            time = j.data.time.epoch2HRDateTime(time)
            line.extend([time, state])
            out.append("|".join(line) + '|')

    out = '\n'.join(out)
    params.result = (out, doc)

    return params
