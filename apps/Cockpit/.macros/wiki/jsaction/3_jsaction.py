
def main(j, args, params, tags, tasklet):
    import urllib
    doc = args.doc
    out = list()
    state = args.getTag('state')
    state = state.upper() if state else None

    actionrunids = [runid.decode() for runid in j.core.db.keys('actions.*') if runid != b'actions.runid']

    # this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n")

    fields = ['Action RunID', 'Action Key', 'State']
    out.append('||Action RunID||Action Key||State||')

    for actionrunid in actionrunids:
        runid = actionrunid.split('actions.')[1]
        for actionkey, actiondetails in j.core.db.hgetall(actionrunid).items():
            actionkey = actionkey.decode()
            actionkeyescaped = actionkey.replace(' ', '___')
            actionkeyescaped = actionkeyescaped.replace("'", "__SINGLEQUOTE__")
            actionkeyescaped = urllib.parse.quote(actionkeyescaped)
            actionstate = j.data.serializer.json.loads(actiondetails)['_state']
            if state:
                if actionstate != state:
                    continue
            line = ['']
            for field in fields:
                if field == 'Action Key':
                    line.append('[%(actionkey)s | /cockpit/action?runid=%(runid)s&actionkey=%(actionkeyescaped)s]'
                                % ({'runid': runid, 'actionkey': actionkey, 'actionkeyescaped': actionkeyescaped}))

                elif field == 'Action RunID':
                    line.append(runid)
                elif field == 'State':
                    line.append(actionstate)

            line.append('')
            out.append("|".join(line))

    out = '\n'.join(out)
    params.result = (out, doc)

    return params
