from JumpScale import j

from .Repo import RepoMgmt
from .Blueprint import BlueprintMgmt
from .Service import ServiceMgmt

import telegram
from telegram.ext import Updater
from telegram.ext.dispatcher import run_async
from telegram.ext import CommandHandler, RegexHandler
from telegram.ext import MessageHandler, Filters
import time
import re
import sys
import redis
import gevent
from gevent import monkey
monkey.patch_all()

import logging
logging.basicConfig(level=logging.DEBUG, format='[+][%(levelname)s] %(name)s: %(message)s')


class TGBot():

    # initializing
    def __init__(self, token, rootpath='', redis=None):
        self.token = token

        if rootpath=="":
            rootpath=j.sal.fs.joinPaths(j.dirs.codeDir, "cockpit", "project")
            j.sal.fs.createDir(rootpath)

        self.rootpath = rootpath
        self.logger = j.logger.get('j.app.cockpit.bot')

        self.logger.debug("projects will be saved to: %s" % rootpath)
        j.sal.fs.createDir(rootpath)

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

        # commands
        dispatcher.addHandler(CommandHandler('start', self.start_cmd))
        dispatcher.addHandler(CommandHandler('repo', self.repo_mgmt.handler, pass_args=True))
        dispatcher.addHandler(CommandHandler('blueprint', self.blueprint_mgmt.handler, pass_args=True))
        dispatcher.addHandler(CommandHandler('service', self.service_mgmt.handler, pass_args=True))
        dispatcher.addHandler(CommandHandler('help', self.help_cmd))

        # messages
        dispatcher.addHandler(MessageHandler([Filters.text], self.message_cmd))

        # internal
        dispatcher.addHandler(RegexHandler(r'/.*', self.unknown_cmd))

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
            gevent.sleep(0.001)

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
            # we only listen to ouput event
            # to send message to client
            return
        self.logger.debug("event recieve telegram output")

        chat_id = evt.args['chat_id']
        msg = evt.args['msg']
        msg = self._sanitize_md(msg)
        self.bot.sendMessage(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

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
            "`/project` - `/blueprint` - `/ays`",
            "",
            "*/project*: let you manage your differents projects (or repository)",
            " - `/project [name]`: will move your current project to `[name]`, if it doesn't exists it will be created",
            " - `/project delete [name]`: will delete the project `[name]`",
            " - `/project list`: will show you your projects list",
            "",
            "When you are ready with your project, simply upload me some blueprint, they will be put on your services repository",
            "",
            "*/blueprint*: will manage the project's blueprints",
            " - `/blueprint list`: will show you your project's blueprint saved",
            " - `/blueprint delete [name]`: will delete the blueprint `[name]`",
            " - `/blueprint delete all`: will delete all the blueprints in your project",
            " - `/blueprint [name]`: will show you the content of the blueprint `[name]`",
            "",
            "When your blueprints are ready, you can go further:",
            "",
            "*/ays*: will control atyourservice",
            " - `/ays init`: will run 'ays init' in your repository",
            " - `/ays do install`: will run 'ays do install' in your repository",
            " - ...",
            "",
            "This message was given by `/help`, have fun with me !",
        ]

        bot.sendMessage(chat_id=update.message.chat_id, text="\n".join(message), parse_mode=telegram.ParseMode.MARKDOWN)

    # initialize
    def start_cmd(self, bot, update):
        username = update.message.from_user.username

        self.logger.debug("hello from: %s (%s %s) [ID %s]" %
                          (username,
                           update.message.from_user.first_name,
                           update.message.from_user.last_name,
                           update.message.chat_id))

        # creating environment for this user
        userpath = '%s/%s' % (self.rootpath, username)

        if not j.sal.fs.exists(userpath):
            j.sal.fs.createDir(userpath)

        if not self.repo_mgmt.users.get(username):
            hello = "Hello %s !" % update.message.from_user.first_name
            self.repo_mgmt.users[username] = {'current': None, 'projects': []}

        else:
            hello = "Welcome back %s !" % update.message.from_user.first_name

        message = [
            hello,
            "",
            "Let's start:",
            " - create a project with: `/project [name]`",
            " - upload some blueprints",
            " - do a *ays init* with `/ays init`",
            " - do a *ays [stuff]* with `/ays [stuff]`",
            "",
            "For more information, just type `/help` :)"
        ]

        bot.sendMessage(chat_id=update.message.chat_id, text="\n".join(message), parse_mode=telegram.ParseMode.MARKDOWN)

    # project manager
    def unknown_cmd(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

    # management
    def start(self):
        self.updater.start_polling()
        self.logger.info("bot is listening")

    def stop(self):
        self.updater.stop()

    # @run_async
    # def _signal_handler(self):
    #     self.updater.stop()
