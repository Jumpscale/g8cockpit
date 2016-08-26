

def main(j, args, params, tags, tasklet):
    doc = args.doc
    repo_name = args.getTag('aysrepo')
    if not repo_name:
        repo_name = 'ays_cockpit'

    try:
        services = j.apps.cockpit.atyourservice.listServices(repository=repo_name, templatename='os.cockpit', ctx=args.requestContext)[repo_name]
        if len(services) != 1:
            params.result = ("Can't find os.cockpit service", doc)
        else:
            service = list(services.values())[0]
            service = j.apps.cockpit.atyourservice.getService(repository=repo_name, role='os', instance=service['instance'], ctx=args.requestContext)
            service_sshkey = j.apps.cockpit.atyourservice.getService(repository=repo_name, role='sshkey', instance='main', ctx=args.requestContext)

            data = {
                'organization': service['instance_hrd']['oauth.organization'],
                'domain': "%s.%s" % (service['instance_hrd']['dns.domain'], service['instance_hrd']['dns.root']),
                'ssh_port': service['instance_hrd']['ssh.port'],
                'private_key': service_sshkey['instance_hrd']['key.priv'],
                'public_key': service_sshkey['instance_hrd']['key.pub'],
                'ays_repo_url': service['instance_hrd']['ays.repo.url'],
                'shellinbox_url': service['instance_hrd']['shellinabox.url']
            }
            args.doc.applyTemplate(data)
    except Exception as e:
        args.doc.applyTemplate({'error': str(e)})

    params.result = (args.doc, doc)

    return params
