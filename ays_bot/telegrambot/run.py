from JumpScale import j
import telegram
import datetime
from .utils import chunks
from telegrambot.Repo import AYS_REPO_DIR
# from JumpScale.baselib.atyourservice.robot.ActionRequest import *


class RunMgmt(object):

    def __init__(self, bot):
        self.bot = bot
        self.rootpath = bot.rootpath
        self.callbacks = bot.question_callbacks

    #
    # # helpers
    # def _blueprintsPath(self, repo):
    #     return '%s/%s/%s/blueprints' % (self.rootpath, repo)

    def _currentRepoName(self, username):
        return self.bot.repo_mgmt._currentRepoName(username)

    def _currentRepo(self, username):
        return j.atyourservice.repoGet(j.sal.fs.joinPaths(AYS_REPO_DIR, self._currentRepoName(username)))

    def _createname(self, run):
        return datetime.datetime.fromtimestamp(run.dictFiltered["lastModDate"]).strftime('%c')

    def _runlist(self, username):
        repo = self._currentRepo(username)
        runs_str = self.bot._rediscl.hget('telegrambot.runs', repo.name)
        if not runs_str:
            return []
        runs = j.data.serializer.json.loads(runs_str)
        run_list = []
        for run in runs:
            run = repo.runGet(run)
            name = self._createname(run)
            run_list.append(name)
        return run_list

    def _getrunid(self, name, repo):
        runs = j.data.serializer.json.loads(self.bot._rediscl.hget('telegrambot.runs', repo.name))
        for run_id in runs:
            run = repo.runGet(run_id)
            if self._createname(run).strip() == name.strip():
                return run.key

    # def _currentBlueprintsPath(self, username):
    #     return self._blueprintsPath(self._currentRepoName(username))

    def create(self, bot, update):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        repo = self._currentRepo(username)
        runs = []
        try:
            run = repo.runCreate()
            run.save()
            runs_str = self.bot._rediscl.hget("telegrambot.runs", repo.name)
            if runs_str:
                runs.extend(j.data.serializer.json.loads(runs_str))
            runs.append(run.key)
            self.bot._rediscl.hset("telegrambot.runs", repo.name, j.data.serializer.json.dumps(runs))
            msg = "run for repo %s has completed creation. to execute, use;\n `/run execute`" % repo.name
        except Exception as e:
            msg = 'Error during run creation'
            self.bot.logger.error(e.message)
        finally:
            self.bot.sendMessage(
                chat_id=chat_id,
                text=msg)

    def simulate(self, bot, update, run_id):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        repo = self._currentRepo(username)
        runs = []
        run = repo.runGet(run_id).objectGet()
        self.bot.sendMessage(
            chat_id=chat_id,
            text=run.__str__())

    def execute(self, bot, update, run_id):

        username = update.message.from_user.username
        chat_id = update.message.chat_id
        repo = self._currentRepo(username)
        run = repo.runGet(run_id).objectGet()
        try:
            run.execute()
            msg = "run for repo %s has completed execution. to view services `/service`" % repo.name
        except Exception as e:
            msg = 'Error during run execution,\n Error: %s' % str(e)
            self.bot.logger.error(e.message)
        finally:
            self.bot.sendMessage(
                chat_id=chat_id,
                text=msg)


    def list(self, bot, update, executed=''):

        username = update.message.from_user.username
        repo = self._currentRepo(username)
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        runs = self._runlist(username)
        if executed == 'executed':
            runs = repo.runsList()
        if not runs:
            self.bot.sendMessage(chat_id=update.message.chat_id,
                                 text="Sorry, this repository has not had any runs yet. :(;\n to create one use `/run create`")
            return
        runs_list = []
        for run in runs:
            if executed == 'executed':
                run = self._createname(run)
            runs_list.append('- %s' % run.replace("_", "\_"))

        msg = '\n'.join(runs_list)
        self.bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

    def inspect(self, bot, update, run_id):
        username = update.message.from_user.username
        repo = self._currentRepo(username)
        run = repo.runGet(run_id)
        # data = ''
        data = j.data.serializer.yaml.dumps(run.dictFiltered)

        # for key, value in run.dictFiltered.items():
        #     if key == 'steps':
        #         data += '<b>- steps</b>\n'
        #         for step in value:
        #             data += '    <b>- %s</b>\n' % step['number']
        #             for name, val in step.items():
        #                 data += '        - <b>%s</b>   =  %s \n' % (name, val)
        #         continue
        #     elif key == 'repo':
        #         value = repo.name
        #     elif key == 'lastModDate':
        #         value = self._createname(run)
        #
        #     data += '<b>- %s</b>\n' % key
        #     data += '    - %s\n' % value
        self.bot.sendMessage(
            chat_id=update.message.chat_id,
            text=data,
            parse_mode="HTML",
            reply_markup=telegram.ReplyKeyboardHide())

    def choose_action(self, bot, update):
        self.callbacks[update.message.from_user.username] = self.dispatch_choice
        choices = ['create', 'simulate', 'execute', 'inspect', 'list']
        reply_markup = telegram.ReplyKeyboardMarkup([choices], resize_keyboard=True, one_time_keyboard=True)
        return self.bot.sendMessage(chat_id=update.message.chat_id,
                                    text="What do you want to do ?", reply_markup=reply_markup)

    def dispatch_choice(self, bot, update):
        message = update.message
        username = update.message.from_user.username
        repo = self._currentRepo(username)
        if message.text == 'list':
            self.list(bot, update, repo)
        elif message.text == 'create':
            self.create_prompt(bot, update, repo)
        elif message.text == 'simulate':
            self.simulate_prompt(bot, update, repo)
        elif message.text in ['execute', 'exec']:
            self.execute(bot, update)
        elif message.text in ['inspect', 'see']:
            self.inspect_prompt(bot, update)

    def execute_prompt(self, bot, update):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        repo = self._currentRepo(username)
        run_list = self._runlist(username)

        def cb(bot, update):
            run_id = self._getrunid(update.message.text, repo)
            self.execute(bot, update, run_id)

        self.callbacks[username] = cb
        reply_markup = telegram.ReplyKeyboardMarkup([run_list], resize_keyboar=True, one_time_keyboard=True)
        self.bot.sendMessage(
            chat_id=chat_id,
            text="Click on the run you want to execute",
            reply_markup=reply_markup)

    def inspect_prompt(self, bot, update):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        repo = self._currentRepo(username)
        run_list = self._runlist(username)

        def cb(bot, update):
            run_id = self._getrunid(update.message.text, repo)
            self.inspect(bot, update, run_id)

        self.callbacks[username] = cb
        reply_markup = telegram.ReplyKeyboardMarkup([run_list], resize_keyboar=True, one_time_keyboard=True)
        self.bot.sendMessage(
            chat_id=chat_id,
            text="Click on the run you want to execute",
            reply_markup=reply_markup)

    def simulate_prompt(self, bot, update):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        repo = self._currentRepo(username)
        run_list = self._runlist(username)

        def cb(bot, update):
            run_id = self._getrunid(update.message.text, repo)
            self.simulate(bot, update, run_id)

        self.callbacks[username] = cb
        reply_markup = telegram.ReplyKeyboardMarkup([run_list], resize_keyboar=True, one_time_keyboard=True)
        self.bot.sendMessage(
            chat_id=chat_id,
            text="Click on the run you want to simulate",
            reply_markup=reply_markup)

    # Handler for robot
    def handler(self, bot, update, args):
        username = update.message.from_user.username

        self.bot.logger.debug('service management for: %s' % username)
        if not self.bot.repo_mgmt._userCheck(bot, update):
            return

        if not self._currentRepo(username):
            message = "Sorry, you are not working on a repo currently, use `/repo` to select a repository"
            return self.bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode="Markdown")

        # no arguments
        if len(args) == 0:
            self.choose_action(bot, update)
            return

        if args[0] == "list":
            if len(args) == 1:
                return self.list(bot, update)
            elif len(args) >= 2:
                return self.list(bot, update, args[1])

        if args[0] in ['create', 'add']:
            return self.create(bot, update)
        if args[0] in ["execute", "exec"]:
            if len(args) == 1:
                return self.execute_prompt(bot, update)
            elif len(args) >= 2:
                return self.execute(bot, update, args[1])
        if args[0] in ["simulate", "sim"]:
            if len(args) == 1:
                return self.simulate_prompt(bot, update)
            elif len(args) >= 2:
                return self.simulate(bot, update, args[1])
        if args[0] in ['inspect', 'see', 'show']:
            if len(args) == 1:
                return self.inspect_prompt(bot, update)
            elif len(args) >= 2:
                return self.inspect(bot, update, args[1])
