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
@click.option('--repo', help='path to the ays repo that contains cockpitconfig service', prompt="Please enter the path to the ays repo that contains cockpitconfig service")
def creates_portforwards(repo):
    if not j.sal.fs.exists(repo):
        printErr("%s doesn't exists" % repo)
        return 1
    if not j.sal.fs.isDir(repo):
        printErr("%s is not a directory" % reop)
        return 1

    j.sal.fs.changeDir(repo)

    cuisine = j.tools.cuisine.local
    if not cuisine.command_check('autossh'):
        cuisine.package.install('autossh')

    cockpit_cfg = j.atyourservice.getService(role='cockpitconfig', instance='main')
    remote_address = cockpit_cfg.hrd.getStr('node.addr')
    remote_connection_port = cockpit_cfg.hrd.getStr('ssh.port')
    ports = {
        'influxdb': 8091,
        'mongodb': 27017,
        'redis': 6379,
        'controller': 9066,
        'portal': 82,
        'syncthing': 18384,
    }
    for name, port in ports.items():
        cmd = 'autossh -o "StrictHostKeyChecking no" -NL 0.0.0.0:{remote_port}:localhost:{local_port} root@{remote_address} -p {remote_connection_port}'\
        .format(remote_port=port, local_port=port, remote_address=remote_address, remote_connection_port=remote_connection_port)
        cuisine.processmanager.ensure(name, cmd=cmd)
        cuisine.processmanager.start(name)

if __name__ == '__main__':
    creates_portforwards()
