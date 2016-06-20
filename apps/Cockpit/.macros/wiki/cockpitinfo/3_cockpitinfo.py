

def main(j, args, params, tags, tasklet):
    doc = args.doc
    repo_name = args.getTag('aysrepo')
    if not repo_name:
        repo_name = 'ays_cockpit'

    services = j.apps.system.atyourservice.findServices(repo_name=repo_name, templatename='os.cockpit')
    if len(services) != 1:
        params.result = ("Can't find os.cockpit service", doc)
    else:
        service = services[0]
        domain = service.hrd.getStr('dns.domain')
        ssh_port = service.hrd.getStr('ssh.port')
        organization = service.hrd.getStr('oauth.organization')
        private_key = ''
        for prod in service.producers['sshkey']:
            if prod.instance == 'main':
                private_key = prod.hrd.getStr('key.priv')
        shellinbox_url = service.hrd.getStr('shellinabox.url')

        data = {
            'organization': organization,
            'domain': domain,
            'ssh_port': ssh_port,
            'private_key': private_key,
            'shellinbox_url': shellinbox_url
        }
        args.doc.applyTemplate(data)
        params.result = (args.doc, doc)

    return params
