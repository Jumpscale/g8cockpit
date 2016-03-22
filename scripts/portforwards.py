#!/usr/local/bin/jspython

from JumpScale import j
import click


def printErr(msg):
    msg = '[-]: %s' % msg
    click.echo(click.style(msg, fg='red'))


def printInfo(msg):
    msg = '[+]: %s' % msg
    click.echo(click.style(msg, fg='blue'))


@click.command()
@click.option('--repo', help='path to the ays repo that contains cockpitconfig service')
def creates_portforwards(repo):
    if repo is not None:
        j.sal.fs.changeDir(repo)
        j.atyourservice.basepath = repo

    cockpit_cfg = None
    cockpit_cfg = j.atyourservice.getService(role='cockpitconfig', instance='main', die=False)
    count = 0
    if cockpit_cfg is None and count < 3:
        while cockpit_cfg is None:
            import ipdb; ipdb.set_trace()
            printErr("Can't find service cockpitconfig, are you in the cockpit ays repo ?")
            repo = j.tools.console.askString("Please enter the path to the ays repo that contains cockpitconfig service", defaultparam='', regex=None, retry=2)
            if not j.sal.fs.exists(repo):
                contnue
            j.sal.fs.changeDir(repo)
            j.atyourservice.basepath = repo
            cockpit_cfg = j.atyourservice.getService(role='cockpitconfig', instance='main', die=False)

    cuisine = j.tools.cuisine.local
    if not cuisine.command_check('autossh'):
        cuisine.package.install('autossh')

    remote_address = cockpit_cfg.hrd.getStr('node.addr')
    remote_connection_port = cockpit_cfg.hrd.getStr('ssh.port')
    ports = {
        'influxdb': 8091,
        'mongodb': 27017,
        'redis': 6379,
        'controller': 9066,
        'portal': 82,
        'syncthing': 18384,
        'grafana': 3000,
    }
    for name, port in ports.items():
        cmd = 'autossh -o "StrictHostKeyChecking no" -NL 0.0.0.0:{remote_port}:localhost:{local_port} root@{remote_address} -p {remote_connection_port}'\
        .format(remote_port=port, local_port=port, remote_address=remote_address, remote_connection_port=remote_connection_port)
        cuisine.processmanager.ensure(name, cmd=cmd)
        cuisine.processmanager.start(name)

if __name__ == '__main__':
    creates_portforwards()
