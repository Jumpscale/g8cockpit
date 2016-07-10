from JumpScale import j
import gevent
from gevent import queue

from .event import EventDispatcher
from .recurring import AysRecurring


class AYSBot(object):
    """docstring for bot"""

    def __init__(self, workers_nbr=5, redis=None):
        self.logger = j.logger.get('j.cockpit.bot')
        self.running = False
        self.workers_nbr = workers_nbr
        self._rediscl = redis if redis else j.core.db
        self.event_dispatcher = EventDispatcher(self)
        self.recurring = AysRecurring(self)
        self.workers = []
        self.tasks_queue = queue.JoinableQueue()
        self.tasks_queue2 = queue.JoinableQueue()

    def start(self):
        self.logger.info("start jscockpit bot")
        self.running = True

        for i in range(self.workers_nbr):
            self.workers.append(gevent.spawn(self.worker, i))
            self.workers.append(gevent.spawn(self.worker_single, i))

        self.event_dispatcher.start()
        self.recurring.start()

    def stop(self):
        self.logger.info('jscockpit bot stopping')
        self.running = False
        self.event_dispatcher.stop()
        self.recurring.stop()
        self.tasks_queue.join()
        self.tasks_queue2.join()
        gevent.killall(self.workers)

    def reload_all(self):
        """
        reload_all unload all the services from the memory.
        This has the effect to reload services from scratch next time they are needed.
        """
        self.logger.info("reload_all: empty memory in progress")
        self.event_dispatcher._load_repo_lock.acquire()
        self.recurring._load_repo_lock.acquire()

        # empty loaded services
        self.event_dispatcher._services_events = {}
        self.recurring._services_reccurring = {}
        # unload all repos and services from atyourservice module.
        j.atyourservice.reset()

        self.event_dispatcher._load_repo_lock.release()
        self.recurring._load_repo_lock.release()
        self.logger.info("reload_all: empty memory done.")

        self.logger.info("reload_all: reload recurring and event subscriber services")
        self.event_dispatcher._load_aysrepos()
        self.recurring._load_aysrepos()
        self.logger.info("reload_all: reload done")

    def worker(self, i):
        nbr = i
        self.logger.info('start worker Nr %d' % i)
        while self.running:

            work = self.tasks_queue.get()

            result = {}
            try:
                repo = j.atyourservice.get(work['repo'])
                run = repo.getRun(role=work['role'], instance=work['instance'], action=work['action'], force=work['force'])

                self.logger.debug('worker %d execute action %s for %s!%s in %s' %
                                  (nbr, work['action'], work['role'], work['instance'], work['repo']))
                run.execute()
            except Exception as e:
                self.logger.error('worker %d error during execution of action %s for %s!%s in %s\n%s' %
                                  (nbr, work['action'], work['repo'], work['role'], work['instance'], str(e)))
                result['error'] = str(e)
            finally:
                resp_q = work['resp_q']
                resp_q.put(result)
                self.tasks_queue.task_done()

    def worker_single(self, i):
        nbr = i
        self.logger.info('start worker single Nr %d' % i)
        while self.running:

            work = self.tasks_queue2.get()

            result = {}
            try:
                service = work['service']
                self.logger.debug('worker single %s execute action %s for %s' % (nbr, work['action'], service.key))
                func = service.getAction(work['action'])
                func(service=work['service'], event=work['args'])
            except Exception as e:
                self.logger.error('worker single %d error during execution of action %s for %s: %s' %
                                  (nbr, work['action'], service.key, str(e)))
                result['error'] = str(e)
            finally:
                resp_q = work['resp_q']
                resp_q.put(result)
                self.tasks_queue2.task_done()

    def schedule_action(self, action, repo, role="", instance="", force=False, notify=False, chat_id=None):
        """
        @action: str, name of the action to Execute
        @repo: str, name of the repo to use
        @role: str, role of the services to executes
        @instance: str, instance of the services to executes
        @force: bool, force action or not

        put the action on the worker queue and return a response queue.
        if you care about the response, just get on the queue returned by this method.
        """
        response_queue = queue.Queue(maxsize=1)
        work = {
            'action': action,
            'repo': repo,
            'role': role,
            'instance': instance,
            'force': force,
            'resp_q': response_queue
        }

        self.logger.debug('schedule action %s for %s!%s in %s' % (action, role, instance, repo))
        if notify:
            msg = "Schedule action *%s* on service `%s` instance `%s` in repo `%s`" % (action, role, instance, repo)
            self.send_tg_msg(msg=msg, chat_id=chat_id)

        self.tasks_queue.put(work)
        return response_queue

    def schedule_single_action(self, action, service, args, notify=False, chat_id=None):
        """
        @action: str, name of the action to execute
        @service: Service object, service on which execute the action
        @args, any, argument to pass to the action

        execute a specific action on a service and pass args as argument to the action.
        This is used to execute event actions services subscribe to.
        """
        response_queue = queue.Queue(maxsize=1)
        work = {
            'action': action,
            'service': service,
            'args': args,
            'resp_q': response_queue
        }

        self.logger.debug('schedule action single %s for %s' % (action, service.key))
        if notify:
            msg = "Schedule action *%s* on service `%s` instance `%s` in repo `%s`" % (action, role, instance, repo)
            self.send_tg_msg(msg=msg, chat_id=chat_id)

        self.tasks_queue2.put(work)
        return response_queue

    def handle_action_result(self, q, action, repo, role, instance, notify=False, chat_id=None):
        """
        q is a response queue receive from schedule_action.
        we get the result of the execution and if an error happened, we send telegram event.
        """
        result = q.get()
        msg = None
        if 'error' in result:
            self.logger.error('Error execution of action %s of service %s!%s from repo `%s`: %s' % (action, role, instance, repo, result['error']))
            msg = "Error happened on action *%s* on service `%s` instance `%s` in repo `%s`:\n ```%s```" % (action, role, instance, repo, result['error'])
        elif notify:
            msg = "Action *%s* on service `%s` instance `%s` in repo `%s` executed without error" % (action, role, instance, repo)

        if msg:
            self.send_tg_msg(msg=msg, chat_id=chat_id)

    def send_tg_msg(self, msg, chat_id=None):
        """
        Create a telegram event that The telegram bot will receive and send msg to the telegram users
        """
        out_evt = j.data.models.cockpit_event.Telegram()
        out_evt.io = 'output'
        out_evt.action = 'message'
        msg.replace('**', '*')
        out_evt.args = {
            'chat_id': chat_id,
            'msg': msg
        }
        self._rediscl.publish('telegram', out_evt.to_json())
