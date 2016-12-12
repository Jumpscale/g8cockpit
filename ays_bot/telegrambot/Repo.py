from JumpScale import j
from .utils import chunks
import telegram
import re

AYS_REPO_DIR = j.sal.fs.joinPaths(j.dirs.VARDIR, "cockpit_repos")


class RepoMgmt:

    def __init__(self, bot):
        self.bot = bot
        self.rootpath = bot.rootpath
        self.callbacks = bot.question_callbacks
        self._cuisine = j.tools.cuisine.local
        self.reg_repo = re.compile(r'^[a-zA-Z0-9-_]+$')

    def init_repo(self, update, bot, name, git_url):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        repopath = '%s/%s' % (self.rootpath, name)
        self.bot.logger.debug('initializing repository: %s' % repopath)

        j.atyourservice.repoCreate(repopath, git_url)

        evt = j.data.models.cockpit_event.Telegram()
        evt.io = 'input'
        evt.action = 'repo.create'
        evt.args = {
            'repo_path': repopath
        }
        self.bot.send_event(evt.to_json())

    # Helpers
    def _userCheck(self, bot, update):
        chat_id = update.message.chat_id
        valid = True
        if self.bot._rediscl.hexists('cockpit.telegram.users', update.message.from_user.username):
            data = self.bot._rediscl.hget('cockpit.telegram.users', update.message.from_user.username).decode()
            data = j.data.serializer.json.loads(data)
            if not data.get('access_token', None):
                valid = False
        else:
            valid = False

        if not valid:
            self.bot.sendMessage(chat_id=chat_id,
                                 text="Hello buddy, I don't know you yet, please use /start so we can meet")

        return valid

    def _setCurrentRepo(self, username, name):
        data = self.bot._rediscl.hget('cockpit.telegram.users', username).decode()
        data = j.data.serializer.json.loads(data)
        data['current_repo'] = name
        self.bot._rediscl.hset('cockpit.telegram.users', username, j.data.serializer.json.dumps(data))

    def _currentRepoName(self, username):
        data = self.bot._rediscl.hget('cockpit.telegram.users', username).decode()
        data = j.data.serializer.json.loads(data)
        return data['current_repo']

    # Management of repos
    def checkout(self, bot, update, repo_name, git_url=''):
        self.bot.logger.debug('checking out repo: %s' % repo_name)

        chat_id = update.message.chat_id
        username = update.message.from_user.username
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        # check repo name validity
        if not re.search(self.reg_repo, repo_name):
            message = "Sorry, I don't support this repo name, please name it without any special characters or spaces."
            return self.bot.sendMessage(chat_id=chat_id, text=message)

        # repo already exists
        if repo_name in [rep.name for rep in j.atyourservice.reposList()]:
            self._setCurrentRepo(username, repo_name)
            message = "Repo `%s` exists, it's now your current working repo." % repo_name
            return self.bot.sendMessage(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

        # creating new repo
        self.init_repo(update, bot, repo_name, git_url)
        self._setCurrentRepo(username, repo_name)

        message = "Repo `%s` created, it's now your current working repo." % repo_name
        self.bot.sendMessage(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

    def list(self, bot, update):
        self.bot.logger.debug('listing repos')
        username = update.message.from_user.username
        chat_id = update.message.chat_id

        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        # current repo (working on)
        if not self._currentRepoName(username):
            self.bot.sendMessage(chat_id=chat_id, text="No repo selected now.")
        else:
            self.bot.sendMessage(
                chat_id=chat_id,
                text="Current repo: *%s*" %
                self._currentRepoName(username),
                parse_mode=telegram.ParseMode.MARKDOWN)

        repos = j.atyourservice.reposList()
        # repos list
        if len(repos) == 0:
            message = "You don't have any repo for now, create the first one with: `/repo create [name]`"
            return self.bot.sendMessage(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

        ln = len(repos)
        reposList = ["I have %d repo%s for you:" % (ln, "s" if ln > 1 else "")]

        for repo in repos:
            reposList.append("- %s" % repo.name)

        self.bot.sendMessage(chat_id=chat_id, text="\n".join(reposList))

    def delete(self, bot, update, repo_names):
        self.bot.logger.debug('deleting repos: %s' % ', '.join(repo_names))

        username = update.message.from_user.username
        chat_id = update.message.chat_id

        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        for name in repo_names:
            try:
                repo = j.atyourservice.repoGet(j.sal.fs.joinPaths(AYS_REPO_DIR, name))

            except KeyError:
                message = "Sorry, I can't find any repo named `%s` :/" % name
                reply_markup = telegram.ReplyKeyboardHide()
                self.bot.sendMessage(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup=reply_markup)
                continue

            if name == self._currentRepoName(username):
                self._setCurrentRepo(username, None)

            self.bot.logger.debug('removing repository: %s' % repo.path)
            repo.destroy()
            j.sal.fs.removeDirTree(repo.path)

            message = "Repo `%s` removed" % name
            self.bot.sendMessage(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

    # UI interaction
    def choose_action(self, bot, update):
        self.callbacks[update.message.from_user.username] = self.dispatch_choice
        choices = [
            ['select'],
            ['create', 'list', 'delete']
        ]
        reply_markup = telegram.ReplyKeyboardMarkup(choices, resize_keyboard=True, one_time_keyboard=True)
        return self.bot.sendMessage(chat_id=update.message.chat_id,
                                    text="What do you want to do ?", reply_markup=reply_markup)

    def select_prompt(self, bot, update):
        username = update.message.from_user.username
        def cb(bot, update):
            repo = update.message.text
            if repo not in repos:
                self.bot.sendMessage(chat_id=update.message.chat_id, text="Selected repo doesn't exsits.")
            else:
                self.checkout(bot, update, repo)
        self.callbacks[username] = cb

        repos = sorted([repo.name for repo in j.atyourservice.reposList()])
        reply_markup = telegram.ReplyKeyboardMarkup(list(chunks(repos, 4)),
                                                    resize_keyboard=True,
                                                    one_time_keyboard=True,
                                                    selective=True)

        return self.bot.sendMessage(chat_id=update.message.chat_id,
                                    text="Choose the repo you want to work on.", reply_markup=reply_markup)

    def create_prompt(self, bot, update):
        def cb(bot, update):
            self._ask_url(bot, update, update.message.text)
        self.callbacks[update.message.from_user.username] = cb
        reply_markup = telegram.ReplyKeyboardHide()

        return self.bot.sendMessage(chat_id=update.message.chat_id,
                                    text="Please enter the name of your repo", reply_markup=reply_markup)

    def _ask_url(self, bot, update, repo_name):
        def cb(bot, update):
            self.checkout(bot, update, repo_name, update.message.text)
        self.callbacks[update.message.from_user.username] = cb
        reply_markup = telegram.ReplyKeyboardHide()

        return self.bot.sendMessage(chat_id=update.message.chat_id,
                                    text="Please enter the url of your remote repo", reply_markup=reply_markup)


    def delete_prompt(self, bot, update):
        username = update.message.from_user.username

        def cb(bot, update):
            self.delete(bot, update, [update.message.text])
        self.callbacks[username] = cb

        repos = sorted([r.name for r in j.atyourservice.reposList()])
        reply_markup = telegram.ReplyKeyboardMarkup(
            list(
                chunks(
                    repos,
                    4)),
            resize_keyboard=True,
            one_time_keyboard=True,
            selective=True)
        return self.bot.sendMessage(chat_id=update.message.chat_id,
                                    text="Please enter the name of the repo you want to delete",
                                    reply_markup=reply_markup)

    def dispatch_choice(self, bot, update):
        message = update.message
        if message.text == "select":
            self.select_prompt(bot, update)
        if message.text == "create":
            self.create_prompt(bot, update)
        elif message.text == 'list':
            self.list(bot, update)
        elif message.text == 'delete':
            self.delete_prompt(bot, update)

    # Handler for robot
    def handler(self, bot, update, args):
        username = update.message.from_user.username
        self.bot.logger.debug('repo management for: %s' % username)
        if not self._userCheck(bot, update):
            return

        # no arguments
        if len(args) == 0:
            return self.choose_action(bot, update)
        else:
            # repo create
            if args[0] == "add" or args[0] == "create":
                if len(args) == 1:
                    return self.create_prompt(bot, update)
                if len(args) > 1:
                    return self.checkout(bot, update, args[1])
            # repos list
            if args[0] == "list":
                return self.list(bot, update)

            # repos select
            if args[0] == "select" and len(args) == 1:
                return self.select_prompt(bot, update)

            if args[0] == "select" and len(args) > 1:
                return self.checkout(bot, update, args[1])

            # repos delete
            if (args[0] == "delete" or args[0] == "remove") and len(args) == 1:
                return self.delete_prompt(bot, update)

            if (args[0] == "delete" or args[0] == "remove") and len(args) > 1:
                args.pop(0)
                return self.delete(bot, update, args)
