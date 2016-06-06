from JumpScale import j
import gevent


class AysRecurring:

    def __init__(self, bot):
        self.bot = bot
        self._gls = []
        self._rediscl = bot._rediscl
        self._pubsub = None
        self._services_reccurring = {}

        self._load_repo_lock = gevent.lock.BoundedSemaphore()

    def start(self):
        self._gls.append(gevent.spawn(self._watch_aysrepos))
        self._gls.append(gevent.spawn(self._recurring_loop))

    def stop(self):
        gevent.killall(self._gls)
        gevent.joinall(self._gls)

    def _recurring_loop(self):
        while self.bot.running is True:

            now = j.data.time.epoch
            with self._load_repo_lock:
                for service, actions in self._services_reccurring.items():
                    for action_name, info in actions.items():

                        sec = j.data.time.getDeltaTime(info['period'])
                        last = info['last']

                        if last is None or now > (last + sec):
                            rq = self.bot.schedule_action(
                                action=action_name,
                                repo=service.aysrepo.name,
                                role=service.role,
                                instance=service.instance,
                                force=True)
                            self._services_reccurring[service][action_name]['last'] = now
                            gevent.spawn(self.bot.handle_action_result, rq, action_name, service.aysrepo.name, service.role, service.instance)

            gevent.sleep(1)

    def _watch_aysrepos(self):
        while self.bot.running:
            self.bot.logger.info("Start looking for services that register recurring actions.")
            self._load_aysrepos()
            gevent.sleep(300)

    def _load_aysrepos(self, repos=[]):
        """
        walk over all the service in repos and look for service that define recurring actions.
        """
        if repos == []:
            repos = j.atyourservice.repos.values()

        for repo in repos:
            for service in repo.findServices():
                for action_name, period in service.state.recurring.items():
                    if service not in self._services_reccurring:
                        self._services_reccurring[service] = {}
                    self._services_reccurring[service][action_name] = {'period': period[0], 'last': None}
                    self.bot.logger.debug("register service recurring from repo %s, service %s, action %s" % (repo.basepath, service.key, action_name))
