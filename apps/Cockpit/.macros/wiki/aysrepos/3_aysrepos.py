

def main(j, args, params, tags, tasklet):
    repos = j.apps.system.atyourservice.listRepos()
    out = []
    for ayspath in repos:
        out.append('h5. AYS Repo: %s' % ayspath)
        for res in ['AYSTemplates', 'AYSInstances', 'AYSBlueprints']:
            out.append('* [%s|cockpit/%s?ayspath=%s]' % (res[3:], res, ayspath))

    out = '\n'.join(out)
    params.result = (out, args.doc)
    return params
