from JumpScale import j
import gevent

from .event import EventDispatcher
from .recurring import AysRecurring


class AYSBot(object):
    """docstring for bot"""

    def __init__(self, redis=None):
        self.logger = j.logger.get('j.cockpit.bot')
        self.running = False
        self._rediscl = redis if redis else j.core.db
        self.event_dispatcher = EventDispatcher(self)
        self.recurring = AysRecurring(self)

    def start(self):
        self.logger.info("start jscockpit bot")
        self.running = True
        self.event_dispatcher.start()
        self.recurring.start()

    def stop(self):
        self.logger.info('jscockpit bot stopping')
        self.running = False
        self.event_dispatcher.stop()
        self.recurring.stop()
