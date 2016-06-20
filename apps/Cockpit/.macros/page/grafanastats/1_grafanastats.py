def main(j, args, params, tags, tasklet):
    page = args.page
    grid = "<iframe id='ifr' width='100%' height='600' src='/grafana/dashboard/db/nodes-stats?var-node=All&theme=light'></iframe>"
    grafana = j.portal.server.active.cfg['grafana']
    if not j.sal.nettools.checkUrlReachable('http://localhost/grafana/'):
        page.addMessage('Grafana is unreachable')
        params.result = page
        return params

    page.addMessage(grid)
    params.result = page
    return params
