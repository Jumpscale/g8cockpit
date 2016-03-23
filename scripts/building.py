#!/usr/local/bin/jspython

from JumpScale import j
import click
import sys

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
@click.option('--host', help='connection string to the host where to build the docker image', default='localhost')
@click.option('--sshkey', help='Name of the ssh key to authorize on the G8Cockpit. key are fetch from ssh-agent.',  default='id_rsa')
def build(host, sshkey):
    """
    Build g8cockpit docker image
    """
    container_name = "cockpit_build"
    image_name = "jumpscale/g8cockpit"

    cuisine = j.tools.cuisine.get(host)

    printInfo("create builder container")
    key_pub = j.do.getSSHKeyFromAgentPub(sshkey)
    container_conn_str = cuisine.docker.ubuntu(name=container_name, image='jumpscale/ubuntu1510', ports="18384:18384", volumes=None, pubkey=key_pub, aydofs=False)

    container = j.tools.cuisine.get(container_conn_str)
    container.package.mdupdate()
    container.installerdevelop.jumpscale8()
    container.portal.install(start=False, minimal=True)
    container.builder.mongodb(start=False)
    container.builder.influxdb(start=False)
    container.builder.grafana(start=False)
    container.run("js 'j.actions.resetAll()'")  # FIXME find why if we don't reset action before installing controller, everything explode
    container.builder.controller(start=False)
    container.builder.caddy(start=False)
    container.package.install('shellinabox')
    bin_path = cuisine.bash.cmdGetPath('shellinaboxd')
    cuisine.file_copy(bin_path, "$binDir")

    printInfo('clean before creating image')
    container.dir_remove("$goDir/src/*")
    container.dir_remove("$tmpDir/*")
    container.dir_remove("$varDir/data/*")

    cuisine.core.run('jsdocker commit -n %s -t %s' % (container_name, image_name))
    cuisine.core.run('jsdocker push -i %s' % image_name)


@click.command()
@click.option('--host', help='connection string to the host where to build the docker image', default='localhost')
@click.option('--sshkey', help='Name of the ssh key to authorize on the G8Cockpit. key are fetch from ssh-agent.', default='id_rsa')
def upgrade(host, sshkey):
    """
    upgrade the jumpscale/g8cockpit docker image.
    Use this when you just want to update last code of jumpscale and not rebuild evrything from scratch
    """
    container_name = "cockpit_build"
    image_name = "jumpscale/g8cockpit"

    cuisine = j.tools.cuisine.get(host)

    printInfo("create builder container")
    key_pub = j.do.getSSHKeyFromAgentPub(sshkey)
    container_conn_str = cuisine.docker.ubuntu(name=container_name, image='jumpscale/g8cockpit', ports="18384:18384", volumes=None, pubkey=key_pub, aydofs=False)
    container = j.tools.cuisine.get(container_conn_str)
    repos = [
        'https://github.com/Jumpscale/ays_jumpscale8.git',
        'https://github.com/Jumpscale/jumpscale_core8.git',
        'https://github.com/Jumpscale/jumpscale_portal8.git',
    ]
    for url in repos:
        j.do.pullGitRepo(url=url, executor=container.executor)
    cuisine.core.run('jsdocker commit -n %s -t %s --force' % (container_name, image_name))
    cuisine.core.run('jsdocker push -i %s' % image_name)

def printErr(msg):
    msg = '[-]: %s' % msg
    click.echo(click.style(msg, fg='red'))

def printInfo(msg):
    msg = '[+]: %s' % msg
    click.echo(click.style(msg, fg='blue'))

def exit(err, code=1):
    if j.application.debug:
        if isinstance(err, BaseException):
            raise(err)
        else:
            raise(RuntimeError(err))
    else:
        sys.exit(code)

# Register Command
cli.add_command(build)
cli.add_command(update)
cli.add_command(upgrade)

if __name__ == '__main__':
    cli()
