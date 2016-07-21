
def main(j, args, params, tags, tasklet):
    doc = args.doc
    ayspath = args.getTag('ayspath')
    out = list()

    # this makes sure bootstrap datatables functionality is used
    out.append('||Repository||Name||')
    for ayspath, templates in j.apps.cockpit.atyourservice.listTemplates(ayspath, ctx=args.requestContext).items():

        templates = sorted(templates, key=lambda template: template['name'])
        for template in templates:

            line = ["|", "[%s|/cockpit/repo?repo=%s]" % (ayspath, ayspath), "|"]
            line.append('[%s|cockpit/Template?ayspath=%s&aysname=%s]' % (template['name'],
                                                                             ayspath, template['name']))
            line.append("|")
            out.append("".join(line))

    out = '\n'.join(out)
    params.result = (out, doc)

    return params
