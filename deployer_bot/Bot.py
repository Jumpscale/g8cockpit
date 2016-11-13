import time
import _thread

from JumpScale import j

from Asker import TelegramAsker
import requests

import telegram
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, RegexHandler, MessageHandler, Filters


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
        self._admin = None
        self._git_url = None

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
    def git_url(self):
        if self._git_url is None:
            self._git_url = self.asker.ask_git_url()
        return self._git_url

    @property
    def admin(self):
        if self._admin is None:
            self._admin = self.asker.ask_admin()
        return self._admin

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
            self._ovc_location = self.asker.ask_ovc_location(
                ovc_client=self.ovc_client, account_name=self.ovc_account, vdc_name=self.ovc_vdc)
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
    ays_client = j.clients.atyourservice.getFromConfig('/optvar/cfg/ays/ays.conf')

    def __init__(self, config):
        self.logger = j.logger.get("j.client.cockpitbot")
        self.config = config
        self.updater = Updater(token=config['bot']['token'])
        self.bot = self.updater.bot
        self.in_progess_args = {}
        self.templates = {
            'welcome': j.sal.fs.fileGetContents('templates/welcome.md'),
            'blueprint': j.sal.fs.fileGetContents('templates/blueprint')
        }
        self.repos = {}
        self.run_key = None  # Holds ays deamon run's key
        self._register_handlers()

    def _register_handlers(self):
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(MessageHandler(Filters.text, self.answer_questions))
        unknown_handler = RegexHandler(r'/.*', self.unknown)
        dispatcher.add_handler(unknown_handler)

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
            self.deploy(username, chat_id, args)
        except Exception as e:
            self.logger.error(e)
            self.bot.sendMessage(chat_id=chat_id, text="Error during deployment : %s\n\n Please /start again." % str(e))

    def deploy(self, username, chat_id, args):
        oauth_data = self.oauth(chat_id, args)
        if 'error' in oauth_data:
            self.bot.sendMessage(chat_id=chat_id, text=oauth_data['error'])
            return

        cockpit_blueprint = self.templates['blueprint']
        jwt_key = self.config['oauth'].get('jwt_key', None)
        if jwt_key:
            # needed cause AYS doesn't support loading yaml file with multiline in it.
            jwt_key = jwt_key.replace('\n', '\\n')

        content = cockpit_blueprint.format(g8_url=args.ovc_url,
                                           g8_user=args.ovc_login,
                                           g8_password=args.ovc_password,
                                           cockpit_name=args.ovc_vdc,
                                           g8_location=args.ovc_location,
                                           dns_sshkey_path=self.config['dns'].get('sshkey', None),
                                           full_domain=args.domain,
                                           oauth_organization=args.organization,
                                           cockpit_admin=args.admin,
                                           oauth_secret=oauth_data['client_secret'],
                                           oauth_id=oauth_data['client_id'],
                                           oauth_jwtkey=jwt_key
                                           )

        path = j.sal.fs.getTmpDirPath(create=False)
        git_url = args.git_url
        repo = j.atyourservice.repoCreate(path, git_url=git_url)
        self.repos[username] = repo
        j.sal.fs.writeFile("%s/blueprints/cockpit.yaml" % path, content)

        self.logger.info('Deployment of cockpit for user %s in progress' % username)
        repo.init()
        repo.blueprintExecute()
        run = repo.runCreate()
        self.run_key = run.model.key
        self.ays_client.execute_run(run)

        _thread.start_new_thread(self._check_job, (chat_id, username, args))

        msg = "Deployment of your cockpit in progress, please be patient."
        self.bot.sendMessage(chat_id=chat_id, text=msg, reply_markup=telegram.ReplyKeyboardHide())

    def oauth(self, chat_id, args):
        url = "http://%s:%s/oauthurl?organization=%s" % (self.config['oauth']['host'], self.config['oauth']['port'], args.organization)
        resp = requests.get(url)
        resp.raise_for_status()

        info = resp.json()
        msg = "Please click on the following link and authorize us to verify you are part of the organization '%s'\n%s" % (
            args.organization, info['url'])
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

    def _check_job(self, chat_id, username, args):
        stop = False
        while not stop:
            job = j.core.jobcontroller.db.runs.get(self.run_key).objectGet()
            state = job.state
            if state == "error":
                traceback = [log['log'] for log in job.model.logs if log.get('log', None)]
                msg = "Error occurred while trying to deploy {err}.\ntry run /start again".format(err="\n".join(traceback))
                self.bot.sendMessage(chat_id=chat_id,
                                     text=msg)
                stop = True
            elif state == "ok":
                self.bot.sendMessage(chat_id=chat_id,
                                     text="You cockpit deploying is finished you can visit it via {domain}".format(domain=args.domain))
                repo = self.repos[username]
                machine = repo.serviceGet('node', 'cockpit')
                msg = "SSH access: `ssh root@{ipPublic} -p {port}`".format(ipPublic=machine.model.data.ipPublic,
                                                                           port=machine.model.data.sshPort)
                self.bot.sendMessage(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

                sshkey = machine.producers['sshkey'][0]
                msg = 'Here is the sshkey you need to use to connect to your cockpit server using SSH.'
                self.bot.sendMessage(chat_id=chat_id, text=msg)
                self.bot.sendMessage(chat_id=chat_id, text=sshkey.model.data.keyPriv)
                stop = True
            time.sleep(5)
        # deplyement done, remove user fromc cahce
        del self.in_progess_args[username]
        self.logger.info('Deployment of cockpit for user %s done.' % username)
