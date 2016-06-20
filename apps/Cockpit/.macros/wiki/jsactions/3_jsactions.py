
def main(j, args, params, tags, tasklet):
    import urllib
    doc = args.doc
    out = list()
    state = args.getTag('state')
    state = state.upper() if state else None

    actionrunids = [runid.decode() for runid in j.core.db.keys('actions.*') if runid != b'actions.runid']
    out.append('{{html:\n <table class="table table-striped table-bordered"><tr> <th>Action RunID</th><th>Action Key</th><th>State</th></tr>')
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

            out.append('''<tr><td>%(runid)s</td>
                        <td><a href=/cockpit/action?runid=%(runid)s&actionkey=%(actionkeyescaped)s>%(actionkey)s</a></td>
                        <td>%(state)s</td></tr>'''
                       % ({'runid': runid, 'actionkey': actionkey, 'actionkeyescaped': actionkeyescaped, 'state': actionstate}))
    out.append('</table>\n}}')
    out = '\n'.join(out)
    params.result = (out, doc)

    return params
