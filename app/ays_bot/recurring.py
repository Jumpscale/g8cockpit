from JumpScale import j
import gevent


class AysRecurring:

    def __init__(self, bot):
        self.bot = bot
        self._gls = []
        self._rediscl = bot._rediscl
        self._pubsub = None
        self._services_reccurring = {}

        self._load_aysrepos()

    def start(self):
        self._gls.append(gevent.spawn(self._recurring_loop))

    def stop(self):
        gevent.joinall(self._gls)

    def _recurring_loop(self):
        while self.bot.running is True:

            now = j.data.time.epoch
            for service, actions in self._services_reccurring.items():
                for action_name, info in actions.items():

                    sec = j.data.time.getDeltaTime(info['period'])
                    last = info['last']

                    if last is None or now > (last + sec):
                        run = service.aysrepo.getRun(role=service.role, instance=service.instance, action=action_name, force=True)
                        self._services_reccurring[service][action_name]['last'] = now
                        gevent.spawn(run.execute)

            gevent.sleep(1)

    def _load_aysrepos(self, repos=[]):
        """
        walk over all the service in repos and look for service that define recurring actions.
        """
        if repos == []:
            repos = j.atyourservice.repos.values()

        for repo in repos:
            for service in repo.findServices():
                for action_name, period in service.state.recurring.items():
                    if service.key not in self._services_reccurring:
                        self._services_reccurring[service] = {}
                    self._services_reccurring[service][action_name] = {'period': period[0], 'last': None}
