
def main(j, args, params, tags, tasklet):
    import urllib
    tags = j.data.tags.getObject(tagstring=args.cmdstr)
    tags = tags.getDict()
    runid = tags.get('runid')
    actionkey = tags.get('actionkey')

    runid = 'actions.%s' % runid
    actionkey = actionkey.replace("__SINGLEQUOTE__", "'")
    actionkey = actionkey.replace('___', ' ')
    action = j.core.db.hget(runid, actionkey)

    if not action:
        params.result = ('Could not find action with runid: "%s" and actionkey: "%s"' % (runid, actionkey), args.doc)
        return params

    action = j.data.serializer.json.loads(action.decode())
    actionadd = dict()
    for key, value in action.items():
        if key == '_parent':
            actionadd['_parentshow'] = value
            value = value.replace(' ', '___') if value else None
        if isinstance(value, str):
            value = value.replace('|', '\|')
            value = value.replace('[', '\[')
            value = value.replace(']', '\]')
            if key in ['_result']:
                value = value.replace('\\n', '\n')
            if key not in ['_source', 'traceback', 'error', '_result']:
                value = value.replace('\n', ' ')
        if key in '_depkeys':
            value = [{dep: dep.replace(' ', '___')} for dep in action[key]]
        action[key] = value
    action.update(actionadd)
    args.doc.applyTemplate(action)
    params.result = (args.doc, args.doc)
    return params
