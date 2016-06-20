from JumpScale import j
import gevent


class EventDispatcher:

    def __init__(self, bot):
        self.bot = bot
        self._gls = []
        self._rediscl = bot._rediscl
        self._pubsub = None
        self._services_events = {}

        self._load_repo_lock = gevent.lock.BoundedSemaphore()

    def start(self):
        self._pubsub = self._register_event_handlers()
        self._gls.append(gevent.spawn(self.watch_aysrepos))
        self._gls.append(gevent.spawn(self._event_loop))

    def stop(self):
        gevent.killall(self._gls)
        gevent.joinall(self._gls)

    def _event_loop(self):
        """
        This loop reveive all message send on the topic lists
        """
        while self.bot.running is True:
            msg = self._pubsub.get_message(timeout=10)
            if msg is not None:
                # if we arrive here, something is wrong,
                # event handlers should have handled the message already
                self.bot.logger.warning("unhandled message. %s" % msg)

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
        """
        generic event handler, when an event is received,
        we check if a service is subscribed to this kind of event and if yes, we execute the action
        """
        channel = msg['channel'].decode()
        self.bot.logger.debug("event received on channel %s" % channel)
        if channel not in self._services_events.keys():
            self.bot.logger.warning("received event on channel not supported (%s)" % channel)
            return

        # check if any service is subscribe to this event
        # if yes execute registred action
        with self._load_repo_lock:
            for repo, service, action_name in self._services_events[channel]:
                args = msg['data'].decode()
                rq = self.bot.schedule_single_action(action_name, service, args)
                args = j.data.serializer.json.loads(args)
                gevent.spawn(
                    self.bot.handle_action_result,
                    rq, action_name,
                    repo.name,
                    service.role,
                    service.instance,
                    notify=args.get('notify', False),
                    chat_id=args.get('chat_id', False)
                )

    def _event_handler_telegram(self, msg):
        self.bot.logger.debug("event received on channel telegram")
        evt = j.data.models.cockpit_event.Telegram.from_json(msg['data'].decode())

        # this handler is specific action execution trigger from telegram
        if evt.io == 'input':
            if evt.action == 'service.execute':
                keys = ['repo', 'role', 'instance', 'action']
                for k in keys:
                    if k not in evt.args:
                        self.bot.logger.warning("execute action event bad format. Missing %s" % k)
                        return

                repo_name = j.sal.fs.getBaseName(evt.args['repo'])
                rq = self.bot.schedule_action(
                    action=evt.args['action'],
                    repo=repo_name,
                    role=evt.args['role'],
                    instance=evt.args['instance'],
                    force=True,
                    notify=evt.args.get('notify', False),
                    chat_id=evt.args.get('chat_id', False)
                )
                # handle result of the action
                gevent.spawn(
                    self.bot.handle_action_result,
                    rq,
                    evt.args['action'],
                    repo_name,
                    evt.args['role'],
                    evt.args['instance'],
                    notify=evt.args.get('notify', False),
                    chat_id=evt.args.get('chat_id', False)
                )
            elif evt.action == 'bp.create':
                # new blueprint, search for new service that subscribe to event or recurring
                name = j.sal.fs.getBaseName(evt.args['path'])
                repo = j.atyourservice.repos.get(name, None)
                if repo is None:
                    return
                self._load_aysrepos([repo])
                self.bot.recurring._load_aysrepos([repo])

    def watch_aysrepos(self):
        while self.bot.running:
            self.bot.logger.info("Start looking for services that register to events.")
            self._load_aysrepos()
            gevent.sleep(300)

    def _load_aysrepos(self, repos=[]):

        with self._load_repo_lock:

            if self._services_events == {}:
                self._services_events = {
                    'email': set(),
                    'telegram': set(),
                    'alarm': set(),
                    'eco': set(),
                    'generic': set(),
                }

            if repos == []:
                repos = j.atyourservice.repos.values()

            for repo in repos:
                for service in repo.findServices():
                    for event_name, actions in service.state.events.items():
                        if event_name not in self._services_events.keys():
                            self.bot.logger.warning("service %s try to register to non existing event %s" % (service, event_name))
                            continue
                        for action_name in actions:
                            self.bot.logger.debug("register service events from repo %s, service %s" % (repo.basepath, service.key))
                            data = (repo, service, action_name)
                            self._services_events[event_name].add(data)
