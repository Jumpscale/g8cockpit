#!/usr/local/bin/jspython

from JumpScale import j
import click
import sys
import time

@click.group()
@click.option('--debug', default=False, help='enable debug mode', is_flag=True)
def cli(debug):
    j.application.debug = debug


@click.command()
def update():
    printInfo("Update required git repository to last version")
    repos = [
        'https://github.com/Jumpscale/ays_jumpscale8.git',
        'https://github.com/Jumpscale/jumpscale_core8.git'
    ]
    cuisine = j.tools.cuisine.local
    for url in repos:
        j.do.pullGitRepo(url=url, executor=cuisine.executor)

@click.command()
@click.option('--repo-url', help='Url of the git repository where to store the ays repo.')
@click.option('--ovc-url', help='Url of the Gener8 where to deploy cockpit')
@click.option('--ovc-login', help='Login of your account on Gener8 where to deploy cockpit')
@click.option('--ovc-password', help='Password of your account on the Gener8 where to deploy cockpit')
@click.option('--ovc-vdc', help='Name of the Virtual Data center where to deploy the G8Cockpit')
@click.option('--ovc-location', help='Location of the vdc')
@click.option('--dns-login', help='Password of your account on the dns cluster')
@click.option('--dns-password', help='Password of your account on the dns cluster')
@click.option('--dns-name', help='Dns to give to the cockpit. Name will be append with .cockpit.aydo.com')
@click.option('--sshkey', help='Name of the ssh key to authorize on the G8Cockpit. key are fetch from ssh-agent.')
@click.option('--portal-password', help='Admin password of the portal')
@click.option('--expose-ssh', help='Expose ssh of the G8Cockpit over HTTP', is_flag=True)
@click.option('--bot-token', help='Telegram token of your bot')
@click.option('--dev', help='Use staging environment for caddy. Enable this during testing to avoid running up adgains letsencrypt rate limits', is_flag=True)
def install(repo_url, ovc_url, ovc_login, ovc_password, ovc_vdc, ovc_location, dns_login, dns_password, dns_name, sshkey, portal_password, expose_ssh, bot_token, dev):
    """
    Start installation process of a new G8Cockpit
    """
    update()

    cuisine = j.tools.cuisine.local
    tmpl_repo = "https://github.com/0-complexity/g8cockpit.git"

    if not repo_url:
        repo_url = j.tools.console.askString("Url of the git repository where to store the ays repo.", defaultparam='', regex=None, retry=2)

    # connection to Gener8 + get vdc client
    printInfo('Test connectivity to Gener8')
    vdc_cockpit = getVDC(ovc_url, ovc_login, ovc_password, ovc_vdc, ovc_location)

    printInfo('Test connectivity to dns server')
    dns_cl = getDNS(dns_login, dns_password)
    dns_name = registerDNS(dns_name, dns_cl, vdc_cockpit)

    key_pub = getSSHKey(sshkey)

    printInfo('cloning template repo (%s)' % tmpl_repo)
    templateRepo = j.do.pullGitRepo(url=tmpl_repo, executor=cuisine.executor)
    printInfo('cloned in %s' % templateRepo)

    if not repo_url:
        repo_url = j.tools.console.askString("Url of the git repository where to store the ays repo.", defaultparam='', regex=None, retry=2)

    printInfo('cloning cockpit repo (%s)' % repo_url)
    cockpitRepo = j.do.pullGitRepo(url=repo_url, executor=cuisine.executor)
    printInfo('cloned in %s' % cockpitRepo)
    git_cl = j.clients.git.get(cockpitRepo)

    src = j.sal.fs.joinPaths(templateRepo, 'ays_repo')
    dest = j.sal.fs.joinPaths(cockpitRepo, 'ays_repo')
    if not j.sal.fs.exists(src):
        exit("%s doesn't exist. template repo is propably not valid")
    j.sal.fs.copyDirTree(src, dest)
    git_cl.commit('init cockpit repo with templates')
    git_cl.push()  # push init commit and create master branch.

    printInfo("Create cockpit VM")
    if 'cockpit' in vdc_cockpit.machines:
        machine = vdc_cockpit.machines['cockpit']
    else:
        machine = vdc_cockpit.machine_create('cockpit', memsize=2, disksize=50, image='Ubuntu 15.10')
    ssh_exec = machine.get_ssh_connection()

    exists = [pf['publicPort']for pf in machine.portforwardings]
    if '80' not in exists:
        machine.create_portforwarding(80, 80)
    if '443' not in exists:
        machine.create_portforwarding(443, 443)
    if '18384' not in exists:
        machine.create_portforwarding(18384, 18384)  # temporary create portforwardings for syncthing

    printInfo('Authorize ssh key into VM')
    # authorize ssh into VM
    ssh_exec.cuisine.set_sudomode()
    ssh_exec.cuisine.ssh.authorize('root', key_pub)
    # reconnect as root
    ssh_exec = j.tools.executor.getSSHBased(ssh_exec.addr, ssh_exec.port, 'root')

    printInfo("Start installation of cockpit")
    ssh_exec.cuisine.package.mdupdate()
    ssh_exec.cuisine.installerdevelop.jumpscale8()
    ssh_exec.cuisine.builder.mongodb(start=False)
    ssh_exec.cuisine.builder.influxdb(start=False)
    ssh_exec.cuisine.builder.controller(start=False)
    ssh_exec.cuisine.builder.caddy(start=False)
    ssh_exec.cuisine.portal.install(start=False, minimal=True)
    ssh_exec.cuisine.package.install('shellinabox')

    printInfo("Start configuration of cockpit")

    printInfo("Configuration of mongodb")
    ssh_exec.cuisine.dir_ensure("$varDir/db/mongo")
    ssh_exec.cuisine.processmanager.ensure('mongodb', '$binDir/mongod --dbpath $varDir/db/mongo')

    printInfo("Configuration of influxdb")
    ssh_exec.cuisine.dir_ensure("$varDir/db/influx")
    ssh_exec.cuisine.dir_ensure("$varDir/db/influx/meta")
    ssh_exec.cuisine.dir_ensure("$varDir/db/influx/data")
    ssh_exec.cuisine.dir_ensure("$varDir/db/influx/wal")
    content = ssh_exec.cuisine.file_read('$varDir/cfg/influxdb/influxdb.conf.org')
    cfg = j.data.serializer.toml.loads(content)
    cfg['meta']['dir'] = "$varDir/db/influx/meta"
    cfg['data']['dir'] = "$varDir/db/influx/data"
    cfg['data']['wal-dir'] = "$varDir/db/influx/data"
    ssh_exec.cuisine.file_write('$varDir/cfg/influxdb/influxdb.conf', j.data.serializer.toml.dumps(cfg))
    ssh_exec.cuisine.processmanager.ensure('influxdb', '$binDir/influxd -config $varDir/cfg/influxdb/influxdb.conf')

    printInfo("Configuration of g8os controller")
    if ovc_url == 'www.mothership1.com':
        ssh_exec.cuisine.builder._startController()
        for pf in machine.portforwardings:
            if pf['publicPort'] == "18384":
                machine.delete_portfowarding_by_id(pf['id'])  # remeove syncthing exposure after controller is configured
                break
    else:
        machine.delete_portforwarding("18384")
    # TODO add jumpscripts ??

    printInfo("Configuration of cockpit portal")
    if not portal_password:
        def validate(passwd):
            if len(passwd) < 6:
                printInfo("Password should be at least 6 characters")
                return False
            return True
        portal_password = j.tools.console.askPassword("Admin password for the portal", confirm=True, regex=None, retry=2, validate=validate)
    ssh_exec.cuisine.portal.start(force=True)

    # wait for the admin user to be created by portal
    timeout = 60
    start = time.time()
    resp = ssh_exec.cuisine.run('jsuser list', showout=False)
    while resp.find('admin') == -1 and start + timeout > time.time():
            time.sleep(2)
            resp = ssh_exec.cuisine.run('jsuser list', showout=False)

    if resp.find('admin') == -1:
        ssh_exec.cuisine.run('jsuser add --data admin:%s:admin:admin@mail.com:cockpit' % portal_password)
    else:
        ssh_exec.cuisine.run('jsuser passwd -ul admin -up %s' % portal_password)

    printInfo("Configuration of shellinabox")
    config = "-s '/:root:root:/:ssh root@localhost'"
    cmd = 'shellinaboxd --disable-ssl --port 4200 %s ' % config
    ssh_exec.cuisine.processmanager.ensure('shellinabox_cockpit', cmd=cmd)

    printInfo("Configuration of caddy proxy")
    shellinbox_url = caddy_cfg(ssh_exec.cuisine, dns_name)
    cmd = '$binDir/caddy -conf $varDir/cfg/caddy/caddyfile'
    if dev:  # enable stating environment
        cmd += ' -ca https://acme-staging.api.letsencrypt.org/directory'
    ssh_exec.cuisine.processmanager.ensure('caddy', cmd)

    token = create_robot(bot_token)
    cmd = "js 'j.atyourservice.telegramBot(\"%s\")'"  % token
    ssh_exec.cuisine.processmanager.ensure('aysrobot', cmd)

    print("Generate cockpit config service")
    pwd = j.sal.fs.getcwd()
    j.sal.fs.changeDir(j.sal.fs.joinPaths(cockpitRepo, 'ays_repo'))
    args = {
        'dns': dns_name,
        'node.addr': ssh_exec.addr,
        'ssh.port': ssh_exec.port,
        'bot.token': token,
    }
    r = j.atyourservice.getRecipe('cockpitconfig')
    r.newInstance(args=args)
    git_cl.commit('add cockpitconfig')
    git_cl.push()
    ssh_exec.cuisine.git.pullRepo(repo_url, branch='master', ssh=False)
    j.sal.fs.changeDir(pwd)

    # execute portforwardings
    script = j.sal.fs.joinPaths(j.sal.fs.getDirName(__file__),'portforwards.py')
    cmd = 'jspython %s --repo %s' % (script, j.sal.fs.joinPaths(cockpitRepo,'ays_repo'))
    cuisine.run(cmd)

    printInfo("\nCockpit deployed")
    printInfo("SSH: ssh root@%s -p %s" % (dns_name, ssh_exec.port))
    printInfo("Shellinabox: https://%s/%s" % (dns_name, shellinbox_url))
    printInfo("Portal: https://%s" % (dns_name))


def printErr(msg):
    msg = '[-]: %s' % msg
    click.echo(click.style(msg, fg='red'))

def printInfo(msg):
    msg = '[+]: %s' % msg
    click.echo(click.style(msg, fg='blue'))

def getVDC(url, login, passwd, vdc_name, location):
    vdc = None
    if not url:
        url = j.tools.console.askString("Url of the Gener8 where to deploy cockpit", defaultparam='', regex=None, retry=2)
    if not login:
        login = j.tools.console.askString("Login of your account on Gener8 where to deploy cockpit", defaultparam='', regex=None, retry=2)
    if not passwd:
        passwd = j.tools.console.askPassword("Password of your account on the Gener8 where to deploy cockpit", confirm=True, regex=None, retry=2, validate=None)
    if not vdc_name:
        vdc_name = j.tools.console.askString("Name of the Virtual Data center where to deploy the G8Cockpit", defaultparam='default', regex=None, retry=2)

    try:
        ovc_cl = j.clients.openvcloud.get(url, login, passwd)

        if len(ovc_cl.locations) == 1:
            location = ovc_cl.locations[0]['name']
        else:
            if not location:
                location = j.tools.console.askString("Location of the vdc", defaultparam='', regex=None, retry=2, validate=None)

        if len(ovc_cl.accounts) == 1:
            account = ovc_cl.accounts[0]
        else:
            resp = j.tools.console.askChoice(ovc_cl.accounts, descr='Choose which account to use', sort=True, maxchoice=60, height=40, autocomplete=False)
            account = ovc_cl.account_get(resp)
        vdc = account.space_get(vdc_name, location, create=True)
    except Exception as e:
        printErr("Error While Trying to connec to Gener8 (%s). account:%s, vdc:%s" % (url, login, vdc_name))
        exit(e)

    return vdc

def getDNS(login, passwd):
    client = None
    if not login:
        login = j.tools.console.askString("Login of your account on the DNS cluster", defaultparam='', regex=None, retry=2)
    if not passwd:
        passwd = j.tools.console.askPassword("Password of your account on the DNS cluster", confirm=True, regex=None, retry=2)

    url = 'https://dns%d.aydo.com/etcd'
    for i in range(1, 4):
        try:
            baseurl = url % i
            client = j.clients.skydns.get(baseurl, username=login, password=passwd)
            _ = client.getConfig()
            return client
        except Exception as e:
            if i > 3:
                printErr("Can't connect to DNS")
                exit(e)
            else:
                continue
    if not client:
        printErr("Can't connect to DNS")
        exit("Can't connect to DNS")


def registerDNS(dns_name, dns_cl, vdc_cockpit):
    def validateDNS(dns_name):
        printInfo("Test if dns name is available (%s)" % dns_name)
        exists, host = dns_cl.exists(dns_name)
        if exists and host != vdc_cockpit.model['publicipaddress']:
            printErr("%s is not available, please choose another name")
            return False
        else:
            return True
    if not dns_name:
        dns_name = j.tools.console.askString("Dns name to give to the cockpit", defaultparam='', regex=None, retry=2)
    while (validateDNS(dns_name) is False):
        dns_name = j.tools.console.askString("Dns name to give to the cockpit", defaultparam='', regex=None, retry=2)

    if not dns_name.endswith('.barcelona.aydo.com'): # TODO chagne DNS
        dns_name = '%s.barcelona.aydo.com' % dns_name
    dns_cl.setRecordA(dns_name, vdc_cockpit.model['publicipaddress'], ttl=120) # TODO, set real TTL
    return dns_name

def getSSHKey(name):
    def validate(name):
        if not name:
            return False
        return True

    if not name:
        name = j.tools.console.askString("Name of the ssh key to authorize on the G8Cockpit. key are fetch from ssh-agent.", defaultparam='id_rsa', regex=None, retry=3, validate=validate)
    return j.do.getSSHKeyFromAgentPub(name)

def caddy_cfg(cuisine, hostname):
    url = j.data.idgenerator.generateXCharID(15)
    tmpl = """
$hostname
gzip

log /optvar/cfg/caddy/log/portal.access.log
errors {
    log /optvar//cfg/caddy/log/portal.errors.log
}

# shellinabox
proxy /$url 127.0.0.1:4200 {
   without /$url
}

# portal
# proty to / need to be last declared proxy
proxy / 127.0.0.1:82

"""
    tmpl = tmpl.replace("$hostname", hostname)
    tmpl = tmpl.replace("$url", url)
    cuisine.file_write('$varDir/cfg/caddy/caddyfile', tmpl)
    cuisine.dir_ensure('$varDir/cfg/caddy/log', tmpl)
    return url

def create_robot(token):
    printInfo("AtYourService Robot creation")
    printInfo("Please connect to telegram and talk to @botfather.")
    printInfo("execute the command /newbot and choose a name and username for your bot")
    printInfo("@botfather should give you a token, paste it here please :")
    if not token:
        token = j.tools.console.askString("Token", defaultparam='', regex=None, retry=2, validate=None)
    printInfo("add command description to your bot.")
    printInfo("type '/setcommands' in @botfather, choose your bot and past these lines :")
    print("""start - create your private environment
project - manage your project (create, list, remove)
blueprint - manage your blueprints project (list, get, remove)
ays - perform some atyourservice actions on your project
help - show you what I can do""")
    resp = j.tools.console.askYesNo("is it done ?")
    while not resp:
        print("please do it")
        resp = j.tools.console.askYesNo("is it done ?")

    return token


def exit(err, code=1):
    if j.application.debug:
        if isinstance(err, BaseException):
            raise(err)
        else:
            raise(RuntimeError(err))
    else:
        sys.exit(code)

# Register Command
cli.add_command(install)
cli.add_command(update)

if __name__ == '__main__':
    cli()
