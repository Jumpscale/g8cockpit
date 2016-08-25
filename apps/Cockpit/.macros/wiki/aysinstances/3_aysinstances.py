from JumpScale.portal.portal import exceptions


def main(j, args, params, tags, tasklet):
    doc = args.doc
    ayspath = args.getTag('ayspath')
    params.merge(args)

    actor = j.apps.actorsloader.getActor("cockpit", "atyourservice")
    out = []
    try:
        for _, services in actor.listServices(ayspath, ctx=args.requestContext).items():
            out.extend(services)
        args.doc.applyTemplate({'services': out})
    except exceptions.BaseError as e:
        args.doc.applyTemplate({'error': e.msg})

    params.result = (args.doc, args.doc)

    return params
