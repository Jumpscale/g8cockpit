
def main(j, args, params, tags, tasklet):
    doc = args.doc
    id = args.getTag('id')
    width = args.getTag('width')
    height = args.getTag('height')
    result = "{{jgauge width:%(width)s id:%(id)s height:%(height)s val:%(running)s start:0 end:%(total)s}}"
    running = list()
    [running.append(len(dockerhosts)) for dockerhosts in j.apps.cockpit.atyourservice.listServices(role='dockerhost', ctx=args.requestContext).values()]

    total = 45
    result = result % {'height': height,
                       'width': width,
                       'running': sum(running),
                       'id': id,
                       'total': total}
    params.result = (result, doc)
    return params
