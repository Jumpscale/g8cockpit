
def main(j, args, params, tags, tasklet):
    doc = args.doc

    out = list()

    dockerhosts = j.apps.cockpit.atyourservice.listServices(role='node')

    if not any(dockerhosts.values()):
        out = 'no Dockerhosts running on this enviroment'
        params.result = (out, args.doc)
        return params

    out.append('||Instance||STATUS||AYS Repo||')
    for ayspath, dockerhostinstances in dockerhosts.items():
        for dockerhost in dockerhostinstances.values():
            out.append('|[%s|/cockpit/dockerhost?ayspath=%s&dockerhost=%s]|N/A|%s|' % (dockerhost.instance,
                                                                                       ayspath, dockerhost.instance,
                                                                                       ayspath))
    out = '\n'.join(out)
    params.result = (out, doc)

    return params
