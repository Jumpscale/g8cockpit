# from gevent import monkey; monkey.patch_all()
from gevent.wsgi import WSGIServer
from gevent.event import Event
import gevent
import signal
import sys
from JumpScale import j

import ays_api
import webhooks_api
import telegrambot
import mail
import falcon_api
import ays_bot


def signal_shutdown():
    raise KeyboardInterrupt


class ServerRack(object):

    def __init__(self, servers):
        self.servers = servers
        self.logger = j.logger.get('j.app.cockpit')

    def start(self):
        started = []
        try:
            for server in self.servers[:]:
                server.start()
                started.append(server)
                name = getattr(server, 'name', None) or server.__class__.__name__ or 'Server'
                self.logger.info('%s started', name)
        except:
            self.stop(started)
            raise

    def stop(self, servers=None):
        if servers is None:
            servers = self.servers[:]
        for server in servers:
            try:
                name = getattr(server, 'name', None) or server.__class__.__name__ or 'Server'
                self.logger.info('%s stopping', name)
                server.stop()
                self.logger.info('%s stopped', name)
            except:
                if getattr(server, 'loop', None):  # gevent >= 1.0
                    server.loop.handle_error(server.stop, *sys.exc_info())
                else:  # gevent <= 0.13
                    import traceback
                    traceback.print_exc()

if __name__ == '__main__':
    if j.core.db.get("cockpit.config.telegram.token")==None:
        doc="""
        AtYourService Robot creation
        Please connect to telegram and talk to @botfather.
        execute the command /newbot and choose a name and username for your bot
        @botfather should give you a token, paste it here please.
        """

        print(doc)
        token=j.tools.console.askString("Bot token")
        j.core.db.set("cockpit.config.telegram.token",token)

    token=j.core.db.get("cockpit.config.telegram.token").decode().strip()


    # start all sub servers
    rack = ServerRack([
        WSGIServer(('', 5000), ays_api.app),
        WSGIServer(('', 5001), webhooks_api.app),
        WSGIServer(('', 5002), falcon_api.app),
        mail.Server(("0.0.0.0", 25)),
        telegrambot.TGBot(token),
        ays_bot.AYSBot(),
    ])
    rack.start()

    # register signal
    forever = Event()
    gevent.signal(signal.SIGTERM, signal_shutdown)

    # wait forever
    try:
        forever.wait()
    except KeyboardInterrupt:
        rack.stop()
