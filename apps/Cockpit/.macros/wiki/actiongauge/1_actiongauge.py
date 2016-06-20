
def main(j, args, params, tags, tasklet):
    doc = args.doc
    id = args.getTag('id')
    width = args.getTag('width')
    height = args.getTag('height')
    result = "{{jgauge width:%(width)s id:%(id)s height:%(height)s val:%(current)s start:0 end:%(total)s}}"

    actionrunids = [runid for runid in j.core.db.keys('actions.*') if runid != b'actions.runid']
    totalactions = dict()
    [totalactions.update(j.core.db.hgetall(runid)) for runid in actionrunids]
    total = len(totalactions) or 24

    failedactions = [action for action, actiondetails in totalactions.items() if j.data.serializer.json.loads(actiondetails)['_state'] == 'ERROR']
    average = total

    current = len(failedactions)

    if average < current:
        average = current

    result = result % {'height': height,
                       'width': width,
                       'id': id,
                       'current': current,
                       'total': average}
    params.result = (result, doc)
    return params
