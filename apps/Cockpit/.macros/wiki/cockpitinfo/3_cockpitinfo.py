

def main(j, args, params, tags, tasklet):
    doc = args.doc
    repo_name = args.getTag('aysrepo')
    if not repo_name:
        repo_name = 'ays_cockpit'

    services = j.apps.system.atyourservice.listServices(repository=repo_name, templatename='os.cockpit', ctx=args.requestContext)[repo_name]
    if len(services) != 1:
        params.result = ("Can't find os.cockpit service", doc)
    else:
        service = list(services.values())[0]
        service = j.apps.system.atyourservice.getService(repository=repo_name, role='os', instance=service['instance'], ctx=args.requestContext)
        domain = service['instance.hrd']['dns.domain']
        ssh_port = service['instance.hrd']['ssh.port']
        organization = service['instance.hrd']['oauth.organization']
        private_key = ''

        service_sshkey = j.apps.system.atyourservice.getService(repository=repo_name, role='sshkey', instance='main', ctx=args.requestContext)
        private_key = service_sshkey['instance.hrd']['key.priv']
        shellinbox_url = service['instance.hrd']['shellinabox.url']

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
