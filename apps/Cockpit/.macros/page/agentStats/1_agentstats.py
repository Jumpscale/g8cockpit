
import json

def main(j, args, params, tags, tasklet):
    page = args.page
    agentid = args.getTag('agentid')
    d = get_list_series(j, agentid=agentid)
    grid = '''
    <script>var d = {d};</script>
    <script>
    var grafanaurl = '{grafana}';
    </script>
    <div id="sel"></div>
    <div>
    <input id="rb1" type="radio" name="dur" value="m" onclick="refresh()" checked/>
    <label for="rb1">minute</label>
    <input id="rb2" type="radio" name="dur" value="h" onclick="refresh()" />
    <label for="rb2">hour</label>
    </div>
    <div id="cbs"></div>
    <div float="right"><iframe id='ifr' width='100%' height='600'></iframe></div>
    '''
    script = '''

    <style>
        .cb { margin: 0 15px 0 0 !important;}        
        .input-wrap { float: left; width: 200px; }
        #ifr { margin: 15px 0 0 0; }
        #rb2 { margin: 0 0 0 5px; }
        #s { width: 100px; margin: 0 0 10px 0;}
    </style>

    <script>
    var init_sel = function(){
        var sel;
        var keys = Object.keys(d)
        if (keys.length == 1){
            sel = '<label>'+keys[0]+'</label><input type="hidden" value="'+keys[0]+'" id="s" />'
        } else {
            sel = '<select id="s" onchange="refresh_cbs()">'+
            keys.map(function(x){return '<option value="'+x+'">'+x+'</option>'}).join('')+
            '</select>'
        
        }
        document.getElementById("sel").innerHTML=sel
    }
    var refresh = function(){

        var dur = Array.prototype.slice.call(document.getElementsByName('dur'),0)
            .filter(function(x){
                return x.checked
            })[0].value;
        document.getElementById('ifr').src=grafanaurl+'/dashboard-solo/script/scriptedagent.js?panelId=1&fullscreen&series='+(Array.prototype.slice.call(document.getElementsByClassName("cb"), 0)
            .filter(function(elem){
                return elem.checked
            })
            .map(function(elem){
                return elem.value+'|'+dur
            })
            .join(','))
    }
    var refresh_cbs=function(){
        var elem = document.getElementById('s');
        document.getElementById("cbs").innerHTML = d[elem.value].map(function(x){
            return '<div class="input-wrap"><input type="checkbox" value="'+elem.value+'|'+x+'" onclick="refresh()" class="cb" />'+x+'</div>'
        }).join('')
    }
    init_sel()
    refresh_cbs()
    refresh()
    </script>
    '''
    grafana = j.portal.server.active.cfg['grafana']
    grafana_url = 'http://%s:%s/' %(grafana['host'],grafana['port'])
    print(grafana_url)
    try:
        j.sal.nettools.checkUrlReachable(grafana_url)
    except:
        page.addMessage('Grafana is unreachable. Make sure it is installed')
        params.result = page
        return params

    grid = grid.format(d=json.dumps(d), grafana=grafana_url)
    grid += script
    page.addMessage(grid)
    params.result = page
    return params


def get_list_series(j, agentid=None):
    influx = j.portal.server.active.cfg['influx']
    client = j.clients.influxdb.get(host=influx['host'], port=influx['port'], database='statistics')
    series = list()
    try:
        series = client.get_list_series()
    except Exception:
        pass
    series = [i['name'].split('|')[0:2] for i in series if i['name'][-1] == 'm']
    hosts = {}
    for i in series:
        arr = hosts.get(i[0], [])
        if not arr:
            hosts[i[0]] = arr
        arr.append(i[1])
    if agentid is None:
        return hosts
    else:
        return {agentid: hosts.get(agentid, [])}
