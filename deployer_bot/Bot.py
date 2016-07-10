from JumpScale import j

from Asker import TelegramAsker
import requests

import telegram
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, RegexHandler, MessageHandler, Filters

import threading
import queue
import logging
import yaml
import glob
import _thread
import time

# class TelegramHandler(logging.Handler):
#     """A Logging handler that send log message to telegram"""
#     def __init__(self, bot, chat_id):
#         super(TelegramHandler, self).__init__()
#         self.bot = bot
#         self.chat_id = chat_id
#         self.msg_tmpl = """
# **{level} :**
# {message}
# """
#
#     def emit(self, record):
#         """
#         Send record to telegram user
#         """
#         try:
#             msg = self.msg_tmpl.format(message=record.getMessage(), level=record.levelname)
#             self.bot.sendMessage(chat_id=self.chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)
#         except Exception as e:
#             pass  # need to always keep running


class CockpitArgs:
    """Argument required to deploy a G8Cockpit"""
    def __init__(self, asker):
        super(CockpitArgs, self).__init__()
        self.logger = j.logger.get("j.client.cockpitbot")

        # Asker is the interface used to ask data to user
        self.asker = asker

        # used by some properties
        self._ovc_client = None

        # Next properties are the actual arguments required by the cockpit
        self._repo_url = None
        self._ovc_url = None
        self._ovc_login = None
        self._ovc_password = None
        self._ovc_account = None
        self._ovc_vdc = None
        self._ovc_location = None
        self._dns_sshkey_path = None
        self._domain = None
        self._sshkey = None
        self._portal_password = None
        self._expose_ssh = None
        self._bot_token = None
        self._gid = None
        self._organization = None


    @property
    def ovc_client(self):
        if self._ovc_client is None:
            try:
                self._ovc_client = j.clients.openvcloud.get(self.ovc_url, self.ovc_login, self.ovc_password)
            except Exception as e:
                msg = "Error while trying to connect to G8 (%s). Login: %s\n%s" % (self.ovc_url, self.ovc_login, str(e))
                self.logger.error(msg)
                self.asker.say(msg)
        return self._ovc_client

    @property
    def repo_url(self):
        if self._repo_url is None:
            self._repo_url = self.asker.ask_repo_url()
        return self._repo_url

    @property
    def ovc_url(self):
        if self._ovc_url is None:
            self._ovc_url = self.asker.ask_ovc_url()
        return self._ovc_url

    @property
    def ovc_login(self):
        if self._ovc_login is None:
            self._ovc_login = self.asker.ask_ovc_login()
        return self._ovc_login

    @property
    def ovc_password(self):
        if self._ovc_password is None:
            self._ovc_password = self.asker.ask_ovc_password()
        return self._ovc_password

    @property
    def ovc_account(self):
        if self._ovc_account is None:
            self._ovc_account = self.asker.ask_ovc_account(self.ovc_client)
        return self._ovc_account

    @property
    def ovc_vdc(self):
        if self._ovc_vdc is None:
            self._ovc_vdc = self.asker.ask_ovc_vdc()
        return self._ovc_vdc

    @property
    def ovc_location(self):
        if self._ovc_location is None:
            self._ovc_location = self.asker.ask_ovc_location(ovc_client=self.ovc_client, account_name=self.ovc_account, vdc_name=self.ovc_vdc)
        return self._ovc_location

    @property
    def domain(self):
        if self._domain is None:
            self._domain = self.asker.ask_domain()
        return self._domain

    @property
    def sshkey(self):
        if self._sshkey is None:
            self._sshkey = self.asker.ask_ssh_key()
        return self._sshkey

    @property
    def portal_password(self):
        if self._portal_password is None:
            self._portal_password = self.asker.ask_portal_password()
        return self._portal_password

    @property
    def expose_ssh(self):
        if self._expose_ssh is None:
            self._expose_ssh = self.asker.ask_expose_ssh()
        return self._expose_ssh

    @property
    def bot_token(self):
        if self._bot_token is None:
            self._bot_token = self.asker.ask_bot_token()
        return self._bot_token

    @property
    def gid(self):
        if self._gid is None:
            self._gid = self.asker.ask_gid()
        return self._gid

    @property
    def organization(self):
        if self._organization is None:
            self._organization = self.asker.ask_organization()
        return self._organization


class CockpitDeployerBot:
    """docstring for """
    def __init__(self):
        self.logger = j.logger.get("j.client.cockpitbot")
        self.config = None
        self.updater = None
        self.bot = None
        self.in_progess_args = {}
        self.templates = {
            'welcome': j.sal.fs.fileGetContents('templates/welcome.md'),
            'blueprint': j.sal.fs.fileGetContents('templates/blueprint')
        }
        self.repos = {}

    def init(self, config):
        self.config = config
        self.updater = Updater(token=config['bot']['token'])
        self.bot = self.updater.bot
        self._register_handlers()
        if 'git' in self.config:
            cuisine = j.tools.cuisine.local
            rc, resp = cuisine.core.run('git config --global user.name', die=False)
            if resp == '':
                cuisine.core.run('git config --global user.name %s' % self.config['git']['username'])
            rc, resp = cuisine.core.run('git config --global user.email', die=False)
            if resp == '':
                cuisine.core.run('git config user.email %s' % self.config['git']['email'])

    def generate_config(self, path):
        """
        generate a default configuration file for the bot
        path: destination file
        """
        cfg = {
            'bot': {'token': 'CHANGEME'},
            'dns': {'sshkey_path': 'CHANGEME'},
            'g8': {
                'be-conv-2': {'address': 'be-conv-2.demo.greenitglobe.com'},
                'be-conv-3': {'address': 'be-conv-3.demo.greenitglobe.com'}
            }
        }
        j.data.serializer.toml.dump(path, cfg)

    def _register_handlers(self):
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('status', self.status))
        dispatcher.add_handler(MessageHandler([Filters.text], self.answer_questions))
        unknown_handler = RegexHandler(r'/.*', self.unknown)
        dispatcher.add_handler(unknown_handler)


    def _attache_logger(self, deployer, chat_id):
        """
        Add a telegram handler to the logger of the deployer objects
        To forward the output of the deployment execution to telegram
        """
        q = queue.Queue()
        qh = logging.handlers.QueueHandler(q)
        qh.setLevel(logging.INFO)
        deployer.logger = j.logger.get('j.clients.cockpit.installer.%s' % chat_id)
        deployer.logger.addHandler(qh)

        th = TelegramHandler(self.bot, chat_id)
        # ql = logging.handlers.QueueListener(q, th)
        # ql.start()
        # return ql

    @run_async
    def answer_questions(self, bot, update, **kwargs):
        username = update.message.from_user.username
        if username in self.in_progess_args:
            args = self.in_progess_args[username]
            args.asker.queue.put(update.message.text)

    @run_async
    def start(self, bot, update, **kwargs):
        chat_id = update.message.chat_id
        username = update.message.from_user.username
        self.logger.info('start command for user %s' % username)

        if username in self.in_progess_args:
            del self.in_progess_args[username]
        args = CockpitArgs(TelegramAsker(self.updater, chat_id, username))
        self.in_progess_args[username] = args

        if 'g8' in self.config:
            choices = [g['address'] for g in self.config['g8'].values()]
            args.asker.g8_choices = choices

        self.bot.sendMessage(chat_id=chat_id, text=self.templates['welcome'].format(username=username))

        try:
            # TODO user multitherading lib
            _thread.start_new_thread(self._check_services_error, (chat_id, username))
            self.deploy(username, chat_id, args)
        except Exception as e:
            self.logger.error(e)
            self.bot.sendMessage(chat_id=chat_id, text="Error during deployment : %s\n\n Please /start again." % str(e))

    def deploy(self, username, chat_id, args):
        oauth_data = self.oauth(chat_id, args)
        if 'error' in oauth_data:
            self.bot.sendMessage(chat_id=chat_id, text=oauth_data['error'])
            return

        path = j.sal.fs.getTmpDirPath()
        repo = j.atyourservice.createAYSRepo(path)
        self.repos[username] = repo

        cockpit_blueprint = self.templates['blueprint']
        jwt_key = self.config['oauth'].get('jwt_key', None)
        if jwt_key:
            # needed cause AYS doesn't support loading yaml file with multiline in it.
            jwt_key = jwt_key.replace('\n', '\\n')

        content = cockpit_blueprint.format(g8_url=args.ovc_url,
                                           g8_account=args.ovc_account,
                                           g8_login=args.ovc_login,
                                           g8_password=args.ovc_password,
                                           telegram_token=args.bot_token,
                                           cockpit_name=args.ovc_vdc,
                                           dns_domain=args.domain,
                                           dns_sshkey_path=self.config['dns'].get('sshkey', None),
                                           oauth_organization=args.organization,
                                           oauth_secret=oauth_data['client_secret'],
                                           oauth_id=oauth_data['client_id'],
                                           oauth_jwtkey=jwt_key,
                                           repo_url=args.repo_url,
                                           )

        msg = "Deployment of you cockpit in progress, please be patient.\nYou can follow progress using the /status command"
        self.bot.sendMessage(chat_id=chat_id, text=msg, reply_markup=telegram.ReplyKeyboardHide())
        self.bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        self.logger.info('Deployment of cockpit for user %s in progress' % username)
        j.sal.fs.writeFile("%s/blueprints/cockpit" % path, content)
        repo.init()
        repo.execute_blueprint(path="%s/blueprints/cockpit" % path)
        repo.install(force=False)

        msg = "Cockpit deployed.\nAddress : https://{url}\nSSH access: `ssh root@{url} -p {port}`".format(
            url=cockpit.hrd.getStr('dns.domain'), port=cockpit.hrd.getInt('ssh.port'))
        self.bot.sendMessage(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

        sshkey = repo.findServices(role='sshkey')[0]
        msg = 'Here is the sshkey you need to use to connect to your cockpit server using SSH.'
        self.bot.sendMessage(chat_id=chat_id, text=msg)
        self.bot.sendMessage(chat_id=chat_id, text=sshkey.hrd.getStr('key.priv'))

        # deplyement done, remove user fromc cahce
        del self.in_progess_args[username]
        self.logger.info('Deployment of cockpit for user %s done.' % username)


    def oauth(self, chat_id, args):
        url = "http://%s:%s/oauthurl?organization=%s" % (self.config['oauth']['host'], self.config['oauth']['port'], args.organization)
        resp = requests.get(url)
        resp.raise_for_status()

        info = resp.json()
        msg = "Please click on the following link and authorize us to verify you are part of the organization '%s'\n%s" % (args.organization, info['url'])
        self.bot.sendMessage(chat_id=chat_id, text=msg)

        # wait for user to login on itsyou.online
        data = j.core.db.blpop(info['state'], timeout=120)
        if data is None:
            msg = "Timeout reached. you didn't authentify on itsyou.online during the last 120 secondes. please /start again"
            return {'error': msg}

        _, data = data
        data = j.data.serializer.json.loads(data)
        return data

    def unknown(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

    def run(self):
        # start polling for telegram bot
        if self.updater is None:
            self.logger.error("connection to telegram bot doesn't exist. please initialise the bot with the init method first.")
            return
        self.updater.start_polling()
        self.logger.info("Bot started")

    def join(self):
        if self.updater is None:
            self.logger.error("connection to telegram bot doesn't exist. please initialise the bot with the init method first.")
            return
        self.updater.idle()
        self.logger.info('stopping bot')

    @run_async
    def status(self, bot, update, **kwargs):
        chat_id = update.message.chat_id
        username = update.message.from_user.username
        if username in self.repos:
            repo = self.repos[username]
        else:
            msg = "Not deployment in progress. start one with the `/start` command"
            self.bot.sendMessage(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)
            return

        try:
            states = []
            for service in repo.services.keys():
                role, instance = service.split("!")
                state = repo.getService(role, instance).state.methods
                for key in state:
                    if state[key] == "ERROR":
                        state[key] = "`ERROR`"
                    states.append('%s:%s:%s' % (service, key, state[key]))
            message_text = ("\n".join(states))
            if message_text:
                self.bot.sendMessage(chat_id=chat_id, text=message_text.replace("_", "-"), parse_mode=telegram.ParseMode.MARKDOWN)
        except Exception as e:
            self.logger.error(e)
            self.bot.sendMessage(chat_id=chat_id, text="Error happened %s" % e)

    def _check_services_error(self, chat_id, username):
        stop = False
        while not stop:
            repo = j.atyourservice.get(username)
            for service in repo.services.keys():
                role, instance = service.split("!")
                state = repo.getService(role, instance).state.methods
                if service == "os!default" and state.get("install", "") == "OK":
                    repo = j.atyourservice.get(username)
                    ip = repo.getService("node", "cockpitvm").hrd.get("publicip")
                    domain = repo.getService("os", "default").hrd.get("dns.domain")
                    self.bot.sendMessage(chat_id=chat_id, text="You cockpit deploying is finished you can visit it via %s" % domain)
                    self.bot.sendMessage(chat_id=chat_id, text="Machine ip address is %s" % ip)
                    stop = True
                    break
                else:
                    for key in state:
                        if state[key] == "ERROR":
                            self.bot.sendMessage(chat_id=chat_id, text="An error occurred try run `/start` again")
                            stop = True
                            break
            if stop:
                break
            time.sleep(5)
