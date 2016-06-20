
def main(j, args, params, tags, tasklet):
    key = args.getTag('key')
    data = j.core.db.hget('webhooks', key)
    data = j.data.serializer.json.loads(data)
    args.doc.applyTemplate({'payload': data})
    params.result = (args.doc, args.doc)
    return params
