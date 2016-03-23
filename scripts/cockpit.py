#!/usr/local/bin/jspython

from JumpScale import j
import click

deployer = None


@click.group()
@click.option('--debug', default=False, help='enable debug mode', is_flag=True)
def cli(debug):
    j.application.debug = debug


@click.command()
def update():
    """
    Update the git repo used during installation of the cockpit.
    Run that before doing install to be sure to have last code.
    """
    printInfo("Update required git repository to last version")
    repos = [
        'https://github.com/Jumpscale/ays_jumpscale8.git',
        'https://github.com/Jumpscale/jumpscale_core8.git',
        'https://github.com/0-complexity/g8cockpit.git'
    ]
    cuisine = j.tools.cuisine.local
    for url in repos:
        j.do.pullGitRepo(url=url, executor=cuisine.executor)


@click.command()
@click.option('--repo-url', help='Url of the git repository where to store the ays repo.')
@click.option('--ovc-url', help='Url of the Gener8 where to deploy cockpit')
@click.option('--ovc-login', help='Login of your account on Gener8 where to deploy cockpit')
@click.option('--ovc-password', help='Password of your account on the Gener8 where to deploy cockpit')
@click.option('--ovc-account', help='Account to use on the Gener8 where to deploy cockpit')
@click.option('--ovc-vdc', help='Name of the Virtual Data center where to deploy the G8Cockpit')
@click.option('--ovc-location', help='Location of the vdc')
@click.option('--dns-login', help='Password of your account on the dns cluster')
@click.option('--dns-password', help='Password of your account on the dns cluster')
@click.option('--domain', help='Dns to give to the cockpit. Name will be append with .cockpit.aydo.com')
@click.option('--sshkey', help='Name of the ssh key to authorize on the G8Cockpit. key are fetch from ssh-agent.')
@click.option('--portal-password', help='Admin password of the portal')
@click.option('--expose-ssh', help='Expose ssh of the G8Cockpit over HTTP', is_flag=True)
@click.option('--bot-token', help='Telegram token of your bot')
@click.option('--gid', help='Grid ID to give to the controller')
@click.option('--dev', help='Use staging environment for caddy. Enable this during testing to avoid running up adgains letsencrypt rate limits', is_flag=True)
def install(repo_url, ovc_url, ovc_login, ovc_password, ovc_account, ovc_vdc, ovc_location, dns_login, dns_password, domain, sshkey, portal_password, expose_ssh, bot_token, gid, dev):
    """
    Start installation process of a new G8Cockpit
    """
    # prepopulate the args with info from CLI
    deployer.args._repo_url = repo_url
    deployer.args._ovc_url = ovc_url
    deployer.args._ovc_login = ovc_login
    deployer.args._ovc_password = ovc_password
    deployer.args._ovc_account = ovc_account
    deployer.args._ovc_vdc = ovc_vdc
    deployer.args._ovc_location = ovc_location
    deployer.args._dns_login = dns_login
    deployer.args._dns_password = dns_password
    deployer.args._domain = domain
    deployer.args._sshkey = sshkey
    deployer.args._portal_password = portal_password
    deployer.args._expose_ssh = expose_ssh
    deployer.args._bot_token = bot_token
    deployer.args._gid = gid


    cockpit_repo_path = deployer.deploy()

    # execute portforwardings
    cmd = 'jspython portforwards.py --repo %s' % j.sal.fs.joinPaths(cockpit_repo_path,'ays_repo')
    printInfo("to enable port forward to your cockpit execute\n%s" % cmd)



def printErr(msg):
    msg = '[-]: %s' % msg
    click.echo(click.style(msg, fg='red'))

def printInfo(msg):
    msg = '[+]: %s' % msg
    click.echo(click.style(msg, fg='green'))


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
    deployer = j.clients.cockpit.installer.getCLI()
    cli()
