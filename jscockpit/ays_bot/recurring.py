from JumpScale import j
import gevent
from . import AYS_REPO_DIR

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
            with self._load_repo_lock:
                for service, actions in self._services_reccurring.items():
                    for action_name, info in actions.items():
                        if 'period' not in info:
                            continue

                        sec = j.data.time.getDeltaTime(info['period'])
                        last = info.get('last', None)

                        now = j.data.time.epoch
                        if last is None or now > (last + sec):
                            rq = self.bot.schedule_action(
                                action=action_name,
                                repo=service.aysrepo.name,
                                role=service.role,
                                instance=service.instance,
                                force=True)

                            self._services_reccurring[service][action_name]['last'] = now
                            service.state.recurring[action_name][1] = now
                            service.state.changed = True
                            service.state.save()

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
            for path in j.atyourservice.findAYSRepos(AYS_REPO_DIR):
                repos.append(j.atyourservice.get(path=path))

        for repo in repos:
            for service in repo.findServices():
                jobs = self._services_reccurring.setdefault(service, {})
                keys = list(jobs.keys())
                for action_name, state in service.state.recurring.items():
                    job = jobs.setdefault(action_name, {})
                    job.update(period=state[0])
                    if action_name in keys:
                        keys.remove(action_name)
                    self.bot.logger.debug("register service recurring from repo %s, service %s, action %s" % (repo.basepath, service.key, action_name))

                for k in keys:
                    jobs.pop(k, None)
