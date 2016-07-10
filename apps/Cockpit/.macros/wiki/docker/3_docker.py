

def main(j, args, params, tags, tasklet):
    docker = args.getTag('docker')
    ayspath = args.getTag('ayspath')

    docker = j.atyourservice.getService('%s!node!%s' % (ayspath, docker))

    link = ('[%s|cockpit/Instance?shortkey=%s&ayspath=%s]' % (docker.instance, docker.key, ayspath))
    link_to_dockerhost = ('[%s|/cockpit/dockerhost?ayspath=%s&dockerhost=%s]' % (docker.parent.instance, ayspath, docker.parent.instance))
    args.doc.applyTemplate({'link': link, 'state': docker.state, 'executor': 'N/A', 'ports': docker.getTCPPorts(), 'parent': link_to_dockerhost})
    params.result = (args.doc, args.doc)
    return params
