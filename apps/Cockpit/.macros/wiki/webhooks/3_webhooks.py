
def main(j, args, params, tags, tasklet):
    hooks = j.core.db.hgetall('webhooks')
    out = ['||Oranization/Repo||Event||Time Stamp||']
    for key, data in hooks.items():
        data = j.data.serializer.json.loads(data)
        event, sha1, time = key.decode().split('.')
        time = j.data.time.epoch2HRDateTime(time)
        info = {'repo': data['repository']['full_name'], 'event': event, 'time': '[%s|/cockpit/webhook?key=%s]' % (time, key.decode())}
        out.append('|%(repo)s|%(event)s|%(time)s|' % info)
    params.result = ('\n'.join(out), args.doc)
    return params
