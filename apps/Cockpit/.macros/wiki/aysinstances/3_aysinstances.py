
def main(j, args, params, tags, tasklet):
    doc = args.doc
    ayspath = args.getTag('ayspath')
    params.merge(args)
    out = []

    actor = j.apps.actorsloader.getActor("system", "atyourservice")

    # this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n")

    fields = ['Role', 'Instance']
    out.append('||Role||Instance||')

    for ayspath, services in actor.listServices(ayspath).items():
        services = sorted(services.values(), key=lambda service: service.role)
        for service in services:
            line = [""]
            for field in fields:
                if field.lower() == 'instance':
                    line.append('[%s|cockpit/AYSInstance?shortkey=%s&ayspath=%s]' % (service.instance,
                                                                                     service.key,
                                                                                     ayspath))
                else:
                    line.append(service.role)

            line.append("")
            out.append("|".join(line))

    params.result = ('\n'.join(out), doc)
    return params
