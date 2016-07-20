
def main(j, args, params, tags, tasklet):
    doc = args.doc

    out = list()
    dockers = j.apps.cockpit.atyourservice.listServices(templatename='node.docker')

    if not any(dockers.values()):
        out = 'No dockers installed'
        params.result = (out, args.doc)
        return params

    out.append('||Instance||STATUS||Path||')
    for ayspath, dockerinstances in dockers.items():
        for docker in dockerinstances.values():
            out.append('|[%s|/cockpit/docker?ayspath=%s&docker=%s]|N/A|%s|' % (docker.instance,
                                                                               ayspath, docker.instance,
                                                                               ayspath))
    out = '\n'.join(out)
    params.result = (out, doc)

    return params
