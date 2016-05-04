# from gevent import monkey; monkey.patch_all()
from gevent.wsgi import WSGIServer
from gevent.event import Event
import gevent
import signal
import sys
from JumpScale import j

import ays_api
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
    token = '205766488:AAHdHmuUuR6mvLDk4YRACcuQiC6zlRJF1Zg'

    # start all sub servers
    rack = ServerRack([
        WSGIServer(('', 5000), ays_api.app),
        telegrambot.TGBot(token),
        mail.Server(("127.1", 25)),
        WSGIServer(('', 5001), falcon_api.app),
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
