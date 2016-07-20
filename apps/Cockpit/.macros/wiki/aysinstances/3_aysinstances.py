
def main(j, args, params, tags, tasklet):
    doc = args.doc
    ayspath = args.getTag('ayspath')
    params.merge(args)
    out = []

    actor = j.apps.actorsloader.getActor("cockpit", "atyourservice")

    # this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n")

    fields = ['Role', 'Instance', 'Repository']
    out.append('||Role||Instance||Repository||')

    for ayspath, services in actor.listServices(ayspath, ctx=args.requestContext).items():
        services = sorted(services, key=lambda service: service['role'])
        for service in services:
            line = [""]
            for field in fields:
                if field.lower() == 'instance':
                    line.append('[%s|cockpit/Instance?shortkey=%s&ayspath=%s]' % (service['instance'],
                                                                                  service['key'],
                                                                                  ayspath))
                else:
                    line.append(service[field.lower()])

            line.append("")
            out.append("|".join(line))

    params.result = ('\n'.join(out), doc)
    return params
