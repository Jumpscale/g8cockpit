#!/usr/local/bin/jspython

from JumpScale import j
import click
import sys


@click.group()
@click.option('--debug', default=False, help='enable debug mode', is_flag=True)
def cli(debug):
    j.application.debug = debug


@click.command()
@click.option('--repo-url', help='Url of the git repository where to store the ays repo.')
@click.option('--ovc-url', help='Url of the Gener8 where to deploy cockpit')
@click.option('--ovc-login', help='Login of your account on Gener8 where to deploy cockpit')
@click.option('--ovc-password', help='Password of your account on the Gener8 where to deploy cockpit')
@click.option('--ovc-vdc', help='Name of the Virtual Data center where to deploy the G8Cockpit')
@click.option('--dns-login', help='Password of your account on the Skydns cluster')
@click.option('--dns-password', help='Password of your account on the Skydns cluster')
@click.option('--dns-name', help='Dns to give to the cockpit. Name will be append with .cockpit.aydo.com')
@click.option('--sshkey', help='Path to public ssh key to authorize on the G8Cockpit')
@click.option('--portal-password', help='Admin password of the portal')
@click.option('--expose-ssh', help='Expose ssh of the G8Cockpit over HTTP', is_flag=True)
def install(repo_url, ovc_url, ovc_login, ovc_password, ovc_vdc, dns_login, dns_password, dns_name, sshkey, portal_password, expose_ssh):
    """
    Start installation process of a new G8Cockpit
    """
    cuisine = j.tools.cuisine.local
    tmpl_repo = "https://github.com/0-complexity/g8cockpit.git"

    if not repo_url:
        repo_url = j.tools.console.askString("Url of the git repository where to store the ays repo.", defaultparam='', regex=None, retry=2)

    # connection to Gener8 + get vdc client
    printInfo('Test connectivity to Gener8')
    vdc_cockpit = getVDC(ovc_url, ovc_login, ovc_password, ovc_vdc)

    printInfo('Test connectivity to Skydns')
    dns_cl = getSkydns(dns_login, dns_password)
    registerDNS(dns_name, dns_cl, vdc_cockpit)

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
    j.sal.fs.copyDirTree(j.sal.fs.joinPaths(templateRepo, 'ays_repo'), j.sal.fs.joinPaths(cockpitRepo, 'ays_repo'))
    git_cl.commit('init cockpit repo with templates')

    printInfo("Create cockpit VM")
    if 'cockpit' in vdc_cockpit.machines:
        machine = vdc_cockpit.machines['cockpit']
    else:
        machine = vdc_cockpit.machine_create('cockpit', memsize=2, disksize=50, image='Ubuntu 15.10')
    ssh_exec = machine.get_ssh_connection()
    printInfo('Authorize ssh key into VM')
    # authorize ssh into VM
    ssh_exec.cuisine.set_sudomode()
    ssh_exec.cuisine.ssh.authorize('root', key_pub)
    # reconnect as root
    ssh_exec = j.tools.executor.getSSHBased(ssh_exec.addr, ssh_exec.port, 'root')
    printInfo("#### Cockpit machine deployed ###")
    printInfo("     SSH: ssh root@%s -p %s" % (dns_name, ssh_exec.port))

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
    # TODO save dns_name in cockpit_config service

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
    ssh_exec.cuisine.builder._startController()
    # TODO add jumpscripts ??

    printInfo("Configuration of cockpit portal")
    if not portal_password:
        def validate(passwd):
            if len(passwd) < 6:
                printInfo("Password should be at least 6 characters")
                return False
            return True
        portal_password = j.tools.console.askPassword("Admin password for the portal", confirm=True, regex=None, retry=2, validate=validate)
    ssh_exec.cuisine.portal.start(portal_password)

    printInfo("Configuration of shellinabox")
    config = "-s '/:root:root:/:ssh root@localhost'"
    cmd = 'shellinaboxd --disable-ssl --port 4200 %s ' % config
    ssh_exec.cuisine.processmanager.ensure('shellinabox_cockpit', cmd=cmd)

    printInfo("Configuration of caddy proxy")
    # TODO generate tls keys
    caddy_cfg(ssh_exec.cuisine, dns_name)
    ssh_exec.cuisine.processmanager.ensure('caddy', '$binDir/caddy -conf $varDir/cfg/caddy/caddyfile')


    # TODO create robot

    from IPython import embed;embed()


def printErr(msg):
    msg = '[-]: %s' % msg
    click.echo(click.style(msg, fg='red'))

def printInfo(msg):
    msg = '[+]: %s' % msg
    click.echo(click.style(msg, fg='blue'))

def getVDC(url, login, passwd, vdc_name):
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
            # TODO @ASK location
            raise("can't decide location,...Not implemented")

        account = ovc_cl.account_get(login)
        vdc = account.space_get(vdc_name, location, create=True)
    except Exception as e:
        import ipdb; ipdb.set_trace()
        printErr("Error While Trying to connec to Gener8 (%s). account:%s, vdc:%s" % (url, login, vdc_name))
        exit(e)

    return vdc

def getSkydns(login, passwd):
    client = None
    if not login:
        login = j.tools.console.askString("Login of your account on the Skydns cluster", defaultparam='', regex=None, retry=2)
    if not passwd:
        passwd = j.tools.console.askPassword("Password of your account on the Skydns cluster", confirm=True, regex=None, retry=2)

    url = 'https://dns%d.aydo.com/etcd'
    for i in range(1, 4):
        try:
            baseurl = url % i
            client = j.clients.skydns.get(baseurl, username=login, password=passwd)
            _ = client.getConfig()
            return client
        except Exception as e:
            if i > 3:
                printErr("Can't connect to Skydns")
                exit(e)
            else:
                continue
    if not client:
        printErr("Can't connect to Skydns")
        exit("Can't connect to Skydns")


def registerDNS(dns_name, dnc_cl, vdc_cockpit):
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
    dns_cl.setRecordA("portal."+dns_name, vdc_cockpit.model['publicipaddress'], ttl=120) # TODO, set real TTL

def getSSHKey(path):
    def validate(path):
        if not j.sal.fs.exists(path):
            printErr("Path %s doesn't exists")
            return False
        # TODO check if key is valid
        return True

    if not path:
        path = j.tools.console.askString("Path to public ssh key to authorize on the G8Cockpit", defaultparam='/root/.ssh/id_rsa.pub', regex=None, retry=2, validate=validate)
    return j.sal.fs.fileGetContents(path)

def caddy_cfg(cuisine, hostname):
    url = j.data.idgenerator.generateXCharID(15)
    # TODO remove :80 when tls key is available
    tmpl = """
portal.$hostname:80 {
    proxy / 127.0.0.1:82
    gzip
    log /optvar/cfg/caddy/log/portal.access.log
    errors {
        log /optvar//cfg/caddy/log/portal.errors.log
    }
}

$hostname:80 {
    proxy /$url 127.0.0.1:4200 {
        without /$url
    }
}
"""
    tmpl = tmpl.replace("$hostname", hostname)
    tmpl = tmpl.replace("$url", url)
    cuisine.file_write('$varDir/cfg/caddy/caddyfile', tmpl)

def create_robot(cuisine):
    printInfo("AtYourService Robot creation")
    printInfo("Please connect to telegram and talk to @botfather.")
    printInfo("execute the command /newbot and choose a name and username for your bot")
    printInfo("@botfather should give you a token, paste it here please :")


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

if __name__ == '__main__':
    cli()
