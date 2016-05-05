from JumpScale import j
import gevent

# from .event import *


class AYSBot(object):
    """docstring for bot"""

    def __init__(self, redis=None):
        self.logger = j.logger.get('j.cockpit.bot')
        self.running = False
        self._rediscl = redis if redis else j.clients.redis.get(ipaddr='localhost', port='6379')
        self.event_handler = EventHandler(self)

    def start(self):
        self.logger.info("start jscockpit bot")
        self.running = True
        self.event_handler.start()

    def stop(self):
        self.running = False


class EventHandler:
    def __init__(self, bot):
        self.bot = bot
        self._rediscl = bot._rediscl
        self._pubsub = None
        self._services_events = {}

        self._load_aysrepos()

    def start(self):
        self._pubsub = self._register_event_handlers()

        while self.bot.running is True:
            msg = self._pubsub.get_message()
            if msg is not None:
                # if we arrive here, something is wrong,
                # event handlers should have handler the message already
                self.bot.logger.warning("unhandled message. %s" % msg)
            gevent.sleep(0.001)

    def _register_event_handlers(self):
        evt_map = {
            'email': self._event_handler,
            'telegram': self._event_handler,
            'telegram': self._event_handler_telegram,
            'alarm': self._event_handler,
            'eco': self._event_handler,
            'generic': self._event_handler,
        }
        ps = self._rediscl.pubsub(ignore_subscribe_messages=True)
        ps.subscribe(**evt_map)
        return ps

    def _event_handler(self, msg):
        channel = msg['channel'].decode()
        self.bot.logger.debug("event received on channel %s" % channel)
        if channel not in self._services_events.keys():
            self.bot.logger.warning("received event on channel not supported (%s)" % channel)
            return

        for repo, service, action_name in self._services_events[channel]:
            j.atyourservice.basepath = repo
            service.getAction(action_name)(force=True)

    def _event_handler_telegram(self, msg):
        self.bot.logger.debug("event received on channel telegram for execute action")
        evt = j.data.models.cockpit_event.Telegram.from_json(msg['data'].decode())

        # this handler is specific action execution trigger from telegram
        if evt.io == 'input':
            if evt.action == 'service.execute':
                self._execute_action(evt, notify_tg=True)
            elif evt.action == 'repo.create':
                self._load_aysrepos([evt.args['repo_path']])

    def _execute_action(self, evt, notify_tg=False):
        keys = ['repo', 'service', 'action']
        for k in keys:
            if k not in evt.args:
                self.bot.logger.warning("execute action event bad format. Missing %s" % k)
                return
        # this needs to be improved, it's too slow.
        # but ays doesn't support anything else at the moment
        j.atyourservice.basepath = evt.args['repo']

        service = j.atyourservice.getServiceFromKey(evt.args['service'])
        action = service.getAction(evt.args['action'])

        # TODO helper method to send data to telegram
        msg = "start execution of action **%s** on service **%s**" % (evt.args['action'], evt.args['service'])
        self.send_tg_msg(chat_id=evt.args['chat_id'], msg=msg)

        # TODO: execute in greenlet
        result = action()

        msg = "result of action **%s** on service **%s**\n\n```\n%s\n```" % (evt.args['action'], evt.args['service'], result)
        self.send_tg_msg(chat_id=evt.args['chat_id'], msg=msg)

    def send_tg_msg(self, chat_id, msg):
        out_evt = j.data.models.cockpit_event.Telegram()
        out_evt.io = 'output'
        out_evt.action = 'message'
        out_evt.args = {
            'chat_id': chat_id,
            'msg': msg
        }
        self._rediscl.publish('telegram', out_evt.to_json())

    def _load_aysrepos(self, repos_path=[]):
        if self._services_events == {}:
            self._services_events = {
                'email': set(),
                'telegram': set(),
                'alarm': set(),
                'eco': set(),
                'generic': set(),
            }

        if repos_path == []:
            repos_path = list(j.atyourservice.findAYSRepos())

        for repo in repos_path:
            self.bot.logger.debug("load service events from repo %s" % repo)
            j.atyourservice.basepath = repo
            for service in j.atyourservice.findServices():
                evts = service.hrd.getDictFromPrefix('events')
                for event_name, actions in evts.items():
                    if event_name not in self._services_events.keys():
                        self.bot.logger.warning("service %s try to register to non existing event %s" % (service, event_name))
                        continue
                    for action_name in actions:
                        data = (repo, service, action_name)
                        self._services_events[event_name].add(data)
