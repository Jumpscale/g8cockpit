import gevent
from gevent import monkey
monkey.patch_all()

from telegrambot.Repo import RepoMgmt
from telegrambot.Blueprint import BlueprintMgmt
from telegrambot.Service import ServiceMgmt
from telegrambot.run import RunMgmt
from telegrambot.utils import chunks

import telegram
from telegram.ext import Updater
from telegram.ext.dispatcher import run_async
from telegram.ext import CommandHandler, RegexHandler
from telegram.ext import MessageHandler, Filters
import time
import re
import sys
import redis
import urllib
from JumpScale import j


STATE_KEY = 'cockpit.ays.state'
MAX_MESSAGE_LENGTH = 4096


class TGBot():

    # initializing
    def __init__(self, config, rootpath='', redis=None):
        self.token = config.get('token', '')
        self.config = config
        self._errmessages = []

        if rootpath == "":
            rootpath = j.sal.fs.joinPaths(j.dirs.VARDIR, "cockpit_repos")
        j.sal.fs.createDir(rootpath)
        j.atyourservice.reposDiscover(rootpath)

        self.rootpath = rootpath
        self.logger = j.logger.get('j.app.cockpit.bot')

        self.logger.debug("projects will be saved to: %s" % rootpath)

        self.question_callbacks = {}

        self.logger.info("initializing telegram bot")
        self.updater = Updater(token=self.token)
        self.bot = self.updater.bot
        dispatcher = self.updater.dispatcher

        # redis
        self._rediscl = redis if redis else j.core.db
        self._register_event_handlers()

        self.logger.debug("make sure ssh-agent is running")
        # if not j.sal.process.checkProcessRunning('ssh-agent'):
        #     j.do.execute('eval `ssh-agent`')

        self.repo_mgmt = RepoMgmt(self)
        self.blueprint_mgmt = BlueprintMgmt(self)
        self.service_mgmt = ServiceMgmt(self)
        self.run_mgmt = RunMgmt(self)

        # commands
        dispatcher.addHandler(CommandHandler('start', self.start_cmd))
        dispatcher.addHandler(CommandHandler('run', self.run_mgmt.handler, pass_args=True))
        dispatcher.addHandler(CommandHandler('repo', self.repo_mgmt.handler, pass_args=True))
        dispatcher.addHandler(CommandHandler('blueprint', self.blueprint_mgmt.handler, pass_args=True))
        dispatcher.addHandler(CommandHandler('service', self.service_mgmt.handler, pass_args=True))
        dispatcher.addHandler(CommandHandler('help', self.help_cmd))

        # messages
        dispatcher.addHandler(MessageHandler([Filters.text], self.message_cmd))

        # internal
        dispatcher.addHandler(RegexHandler(r'/.*', self.unknown_cmd))

    def sendMessage(self, chat_id, text, parse_mode=None, disable_web_page_preview=None, **kwargs):
        for chunk in chunks(text, MAX_MESSAGE_LENGTH):
            send_msg = self.bot.sendMessage(
                chat_id=chat_id,
                text=chunk,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                **kwargs)
        return send_msg

    def _register_event_handlers(self):
        evt_map = {
            'email': self._event_handler,
            'telegram': self._event_handler_telegram,
            'alarm': self._event_handler,
            'eco': self._event_handler,
            'generic': self._event_handler,
        }
        self._pubsub = self._rediscl.pubsub(ignore_subscribe_messages=True)
        self._pubsub.subscribe(**evt_map)
        gevent.spawn(self.evt_loop)

    def evt_loop(self):
        while True:
            msg = self._pubsub.get_message()
            if msg is not None:
                # if we arrive here, something is wrong,
                # event handlers should have handler the message already
                self.logger.warning("unhandled message. %s" % msg)
            gevent.sleep(0.5)

    def _event_handler(self, msg):
        channel = msg['channel'].decode()
        self.logger.debug("event received on channel %s" % channel)
        # TODO: actually do something with the event

    def _sanitize_md(self, msg):
        # telegram Markdown parser use simple * for bold text
        return msg.replace('**', '*')

    def _event_handler_telegram(self, msg):
        evt = j.data.models.cockpit_event.Telegram.from_json(msg['data'].decode())

        if evt.io != 'output':
            # we only listen to ouput event to send message to client
            return

        self.logger.debug("event recieve telegram output")

        if evt.action == 'message':
            self._handle_event_message(evt)
        elif evt.action == 'service.communication':
            gevent.spawn(self._handle_event_service_com, evt)

    def _handle_event_message(self, evt):
        msg = self._sanitize_md(evt.args['msg'])
        chat_ids = set()
        if 'chat_id' in evt.args and evt.args['chat_id'] is not None:
            if evt.args['chat_id']:
                chat_ids.add(evt.args['chat_id'])
        else:
            users = self._rediscl.hgetall('cockpit.telegram.users')
            for _, data in users.items():
                data = j.data.serializer.json.loads(data.decode())
                chat_id = data['chat_id']
                if chat_id:
                    chat_ids.add(chat_id)
        for chat_id in chat_ids:
            try:
                import re

                def normalize_runid(s):
                    """
                    RUN:testg82 111

                    :param s:
                    :return returns a normalized string because it gets a different RUNID on everyrun.
                    """
                    return re.sub("RUN:.+?\n", "NOOOONE", s)

                comparemsg = normalize_runid(msg)
                normalized_msgs = [normalize_runid(x) for x in self._errmessages]

                if "error" in comparemsg.lower():
                    if comparemsg not in normalized_msgs:
                        self.sendMessage(chat_id=chat_id, text=msg, parse_mode=None)
                    self._errmessages.append(msg)
                    if len(self._errmessages) > 20:
                        self._errmessages = self._errmessages[-20:]
                else:  # not an error
                    self.sendMessage(chat_id=chat_id, text=msg, parse_mode=None)

            except Exception as e:
                self.logger.error("Error sending message (chat id %s)'%s' : %s" % (chat_id, msg, str(e)))

    def errorsof_cmd(self, bot, update, args):
        # only the first arg
        arg = args[0]
        errmsgs = "LIST OF ERRORS related to %s:\n" % arg
        if self._errmessages:
            errmsgs += "\n".join(errmsg for errmsg in self._errmessages if arg in errmsg)
            self.sendMessage(chat_id=update.message.chat_id, text=errmsgs)

    def list_errors_cmd(self, bot, update):
        errmsgs = "LIST OF ERRORS:\n"
        if self._errmessages:
            errmsgs += "\n".join(self._errmessages)
            self.sendMessage(chat_id=update.message.chat_id, text=errmsgs)

    def _handle_event_service_com(self, evt):
        # If no key, we can't send response. exit here.
        key = evt.args.get('key', None)
        if key is None:
            return

        # if no username or message, we can't continue
        username = evt.args.get('username', None)
        msg = evt.args.get('message', None)
        channel = evt.args.get('channel', None)
        if not (username or channel) or not msg:
            resp = {'error': 'username/channel or message is empty'}
            self._rediscl.rpush(key, j.data.serializer.json.dumps(resp))
            return

        # search for the chat_id for the username
        if username:
            data = self._rediscl.hget('cockpit.telegram.users', username)
            if data is None:
                # mean we don't know the user.
                resp = {'error': 'user %s not known, the user need to start a chat with the bot first.' % username}
                self._rediscl.rpush(key, j.data.serializer.json.dumps(resp))
                return

            data = j.data.serializer.json.loads(data)
        elif channel:
            data = {'chat_id': '@%s' % channel}

        if evt.args.get('expect_response', True):
            def callback(bot, update):
                # this method is called when the user response.
                # it contains the reponse of the user
                resp = {'response': update.message.text}
                self._rediscl.rpush(key, j.data.serializer.json.dumps(resp))
            self.question_callbacks[username] = callback

        # create keyboard is needed
        keyboard = evt.args.get('keyboard', [])
        if keyboard:
            reply_markup = telegram.ReplyKeyboardMarkup(list(chunks(keyboard, 4)),
                                                        resize_keyboard=True,
                                                        one_time_keyboard=True,
                                                        selective=True)
        else:
            reply_markup = None

        # send message
        try:
            send_msg = self.sendMessage(
                chat_id=data['chat_id'],
                text=msg,
                parse_mode=telegram.ParseMode.HTML,
                reply_markup=reply_markup)
        except Exception as e:
            err_msg = "Error sending message (chat id %s)'%s' : %s" % (data['chat_id'], msg, str(e))
            self.logger.error(err_msg)
            resp = {'error': err_msg}
            self._rediscl.rpush(key, j.data.serializer.json.dumps(resp))
            return

    def send_event(self, payload):
        self._rediscl.publish('telegram', payload)

    @run_async
    def message_cmd(self, bot, update, **kwargs):
        username = update.message.from_user.username
        self.logger.info('%s [%s]: %s' % (username, update.message.chat_id, update.message.text))

        if username in self.question_callbacks:
            self.logger.debug("call back found")
            cb = self.question_callbacks.pop(username)
            cb(bot, update)
            return

        if getattr(update.message, 'document', None):
            self.blueprint_mgmt.document(bot, update)
            return

    def help_cmd(self, bot, update):
        message = [
            "*Okay buddy, this is how I work:*",
            "",
            "At first, you need to run `/start` to let me know you.",
            "",
            "After that, you will be able to run some commands:",
            " `/repo` - `/blueprint` - `run` - `/service`",
            "",
            "*/repo*: let you manage your differents AYS repository",
            "",
            "When you are ready with your project, simply upload me some blueprint, they will be put on your services repository",
            "",
            "*/blueprint*: will manage the project's blueprints",
            "",
            "When your blueprints are ready, you can go further:",
            "",
            "*/run*:will let you control the runs and.",
            "",
            "*/service*: will control your services instances",
            "",
            "This message was given by `/help`, have fun with me !",
        ]

        self.sendMessage(
            chat_id=update.message.chat_id,
            text="\n".join(message),
            parse_mode=telegram.ParseMode.MARKDOWN)

    # initialize
    def start_cmd(self, bot, update):
        username = update.message.from_user.username

        self.logger.debug("hello from: %s (%s %s) [ID %s]" %
                          (username,
                           update.message.from_user.first_name,
                           update.message.from_user.last_name,
                           update.message.chat_id))

        data = None
        data = self._rediscl.hget('cockpit.telegram.users', username)
        if data is not None:
            data = j.data.serializer.json.loads(data.decode())
        if data is None or data.get('access_token', None) is None:
            # user not authenticated
            data = {
                'chat_id': update.message.chat_id,
                'current_repo': None,
                'access_token': None
            }
            resp = self.oauth(bot, update)
            if 'error' in resp:
                return self.endMessage(chat_id=update.message.chat_id, text=resp[
                                       'error'], parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                hello = "You have been authorized. Welcome !"
                data['access_token'] = resp['access_token']
        else:
            hello = "Welcome back %s !" % update.message.from_user.first_name

        data['chat_id'] = update.message.chat_id
        self._rediscl.hset('cockpit.telegram.users', username, j.data.serializer.json.dumps(data))
        message = [
            hello,
            "",
            "Let's start:",
            " - manage your repositories with: `/repo`",
            " - manage your blueprints with: `/blueprint`",
            " - manage your runs with: `/run`",
            " - manage your services with: `/service`",
            " - reload your services with: `/reload`",
            "For more information, just type `/help` :)"
        ]

        self.sendMessage(
            chat_id=update.message.chat_id,
            text="\n".join(message),
            parse_mode=telegram.ParseMode.MARKDOWN)

    # project manager
    def unknown_cmd(self, bot, update):
        self.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

    def oauth(self, bot, update):
        user_id = update.message.from_user.id
        chat_id = update.message.chat_id

        organization = self.config['oauth']['organization']
        random = j.data.idgenerator.generateXCharID(20)
        state = '%s.%s' % (user_id, random)
        self._rediscl.hset(STATE_KEY, state, organization)
        params = {
            'response_type': 'code',
            'client_id': self.config['oauth']['client_id'],
            'redirect_uri': self.config['oauth']['redirect_uri'],
            'state': state,
            'scope': 'user:memberof:%s' % organization
        }
        url = 'https://itsyou.online/v1/oauth/authorize?%s' % urllib.parse.urlencode(params)

        msg = "I don't know you yet, pease click on the following link and authorize us to verify you are part of the organization '%s'\n%s" % (
            organization, url)
        self.sendMessage(chat_id=chat_id, text=msg)

        # wait for user to login on itsyou.online
        data = j.core.db.blpop(state, timeout=120)
        if data is None:
            msg = "Timeout reached. you didn't authentify on itsyou.online during the last 120 secondes. please /start again"
            return {'error': msg}

        _, data = data
        data = j.data.serializer.json.loads(data)
        print(data)
        return data

    # management
    def start(self):
        self.updater.start_polling()
        self.logger.info("bot is listening")

    def join(self):
        if self.updater is None:
            self.logger.error(
                "connection to telegram bot doesn't exist. please initialise the bot with the init method first.")
            return
        self.updater.idle()
        self.logger.info('stopping bot')

    def stop(self):
        self.updater.stop()

    # @run_async
    # def _signal_handler(self):
    #     self.updater.stop()
