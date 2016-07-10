
def main(j, args, params, tags, tasklet):
    doc = args.doc
    ayspath = args.getTag('ayspath')
    out = list()

    # this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n")
    fields = ['Name']

    for ayspath, templates in j.apps.system.atyourservice.listTemplates(ayspath).items():
        out.append('h5. AYSRepo: %s' % ayspath)
        out.append('||Name||')

        templates = sorted(templates, key=lambda template: template['name'])
        for template in templates:
            line = [""]
            line.append('[%s|cockpit/Template?ayspath=%s&aysname=%s]|' % (template['name'],
                                                                             ayspath, template['name']))
            out.append("|".join(line))

    out = '\n'.join(out)
    params.result = (out, doc)

    return params
