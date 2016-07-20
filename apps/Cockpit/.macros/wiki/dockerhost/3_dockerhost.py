

def main(j, args, params, tags, tasklet):
    dockerhost = args.getTag('dockerhost')
    ayspath = args.getTag('ayspath')

    dockerhost = j.apps.cockpit.atyourservice.listServices(repo_path=ayspath)[ayspath]['node!%s' % (dockerhost)]

    link = ('[%s|cockpit/Instance?shortkey=%s&ayspath=%s]' % (dockerhost.instance, dockerhost.key, ayspath))
    children = {}
    for key, dockers in dockerhost.listChildren().items():
        for docker in dockers:
            children[key] = ('[%s|/cockpit/docker?ayspath=%s&docker=%s]' % (docker, ayspath, docker))

    args.doc.applyTemplate({'state': dockerhost.state, 'link': link, 'children': children, 'executor': 'N/A'})
    params.result = (args.doc, args.doc)
    return params
