from JumpScale import j
import telegram
import re
# from JumpScale.baselib.atyourservice.robot.ActionRequest import *


class ProjectMgmt:

    def __init__(self, bot):
        self.bot = bot
        # self.updater = bot.updater
        # self.bot = bot.updater.bot
        self.rootpath = bot.rootpath
        self.users = self.restore()
        self.callbacks = bot.question_callbacks

        self.reg_project = re.compile(r'^[a-zA-Z0-9-_]+$')

    def restore(self):
        usersList = j.sal.fs.listDirsInDir(self.rootpath)
        users = {}

        for user in usersList:
            username = j.sal.fs.getBaseName(user)
            users[username] = {
                'current': None,
                'projects': []
            }

            for project in j.sal.fs.listDirsInDir(user):
                projectName = j.sal.fs.getBaseName(project)
                users[username]['projects'].append(projectName)

        self.bot.logger.debug('users loaded: %s' % users)
        return users

    def init_repo(self, username, project):
        repopath = '%s/%s/%s' % (self.rootpath, username, project)
        self.bot.logger.debug('initializing repository: %s' % repopath)

        j.atyourservice.createAYSRepo(repopath)

        evt = j.data.models.cockpit_event.Telegram()
        evt.io = 'input'
        evt.action = 'repo.create'
        evt.args = {
            'username': username,
            'repo_path': repopath
        }
        self.bot.send_event(evt.to_json())
        # j.sal.fs.createDir(repopath)
        # j.sal.fs.createDir('%s/blueprints' % repopath)
        # j.sal.fs.writeFile('%s/.ays' % repopath, '')

        # previous = j.sal.fs.getcwd()
        # j.sal.fs.changeDir(repopath)

        # initialize empty git repository
        # j.do.execute("git init", showout=False, die=False)

        # j.sal.fs.changeDir(previous)

    # Helpers
    def _userCheck(self, bot, update):
        if not self.users.get(update.message.from_user.username):
            bot.sendMessage(chat_id=update.message.chat_id, text='Hello buddy, please use /start at first.')
            return False

        return True

    def _setCurrentProject(self, username, project):
        self.users[username]['current'] = project

    def _currentProject(self, username):
        return self.users[username]['current']

    def _getProjects(self, username):
        return self.users[username]['projects']

    def _addProject(self, username, project):
        self.users[username]['projects'].append(project)

    def _projectPath(self, username, project):
        return '%s/%s/%s' % (self.rootpath, username, project)

    # Management of projects
    def checkout(self, bot, update, project):
        self.bot.logger.debug('checking out project: %s' % project)

        username = update.message.from_user.username
        chatid = update.message.chat_id

        # check project name validity
        if not re.search(self.reg_project, project):
            message = "Sorry, I don't support this project name, please name it without any special characters or spaces."
            return bot.sendMessage(chat_id=chatid, text=message)

        # notify ays bot need to track that repo
        # req = {
        #     'cmd': REPO_CREATE,
        #     'path': '/opt/code/github/gig-projects/playenv/ays_recurring',
        #     'user_id': update.message.from_user.username,
        #     'chat_id': update.message.chat_id
        # }
        # self.bot.schedule_action(req, now=True)

        # project already exists
        if project in self._getProjects(username):
            self._setCurrentProject(username, project)

            message = "This project already exists, `%s` is now your current working project." % project
            return bot.sendMessage(chat_id=chatid, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

        # creating new project
        self.init_repo(username, project)
        self._setCurrentProject(username, project)
        self._addProject(username, project)

        message = "Project `%s` created, it's now your current working project." % project
        bot.sendMessage(chat_id=chatid, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

    def list(self, bot, update):
        self.bot.logger.debug('listing projects')
        username = update.message.from_user.username
        chatid = update.message.chat_id

        # current project (working on)
        if not self._currentProject(username):
            bot.sendMessage(chat_id=chatid, text="No project selected now.")
        else:
            bot.sendMessage(chat_id=chatid, text="Current project: **%s**" % self._currentProject(username), parse_mode=telegram.ParseMode.MARKDOWN)

        projects = self._getProjects(username)
        # projects list
        if len(projects) == 0:
            message = "You don't have any project for now, create the first one with: `/project [name]`"
            return bot.sendMessage(chat_id=chatid, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

        ln = len(projects)
        projectsList = ["I have %d project%s for you:" % (ln, "s" if ln > 1 else "")]

        for project in projects:
            projectsList.append("- %s" % project)

        bot.sendMessage(chat_id=chatid, text="\n".join(projectsList))

    def delete(self, bot, update, projects):
        self.bot.logger.debug('deleting projects: %s' % projects)

        username = update.message.from_user.username
        chatid = update.message.chat_id

        for project in projects:
            if project not in self._getProjects(username):
                message = "Sorry, I can't find any project named `%s` :/" % project
                bot.sendMessage(chat_id=chatid, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
                continue

            if project == self._currentProject(username):
                self._setCurrentProject(username, None)

            local = self._projectPath(username, project)

            self.bot.logger.debug('removing repository: %s' % local)
            j.sal.fs.removeDirTree(local)
            self.users[username]['projects'].remove(project)

            evt = j.data.models.cockpit_event.Telegram()
            evt.io = 'input'
            evt.action = 'repo.delete'
            evt.args = {
                'username': username,
                'repo_path': local
            }
            self.bot.send_event(evt.to_json())

            message = "Project `%s` removed" % project
            bot.sendMessage(chat_id=chatid, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

    # UI interaction
    def choose_action(self, bot, update):
        self.callbacks[update.message.from_user.username] = self.dispatch_choice
        choices = [
            ['select'],
            ['create', 'list', 'delete']
        ]
        reply_markup = telegram.ReplyKeyboardMarkup(choices, resize_keyboard=True, one_time_keyboard=True)
        return bot.sendMessage(chat_id=update.message.chat_id, text="What do you want to do ?", reply_markup=reply_markup)

    def select_prompt(self, bot, update):
        username = update.message.from_user.username
        projects = self._getProjects(username)

        def cb(bot, update):
            project = update.message.text
            if project not in projects:
                bot.sendMessage(chat_id=update.message.chat_id, text="Selected project doesn't exsits.")
            else:
                self.checkout(bot, update, project)
        self.callbacks[update.message.from_user.username] = cb

        reply_markup = telegram.ReplyKeyboardMarkup([projects], resize_keyboard=True, one_time_keyboard=True, selective=True)
        return bot.sendMessage(chat_id=update.message.chat_id, text="Choose the project you want to work on.", reply_markup=reply_markup)

    def create_prompt(self, bot, update):
        def cb(bot, update):
            self.checkout(bot, update, update.message.text)
        self.callbacks[update.message.from_user.username] = cb
        return bot.sendMessage(chat_id=update.message.chat_id, text="Please enter the name of your project")

    def delete_prompt(self, bot, update):
        username = update.message.from_user.username

        def cb(bot, update):
            self.delete(bot, update, [update.message.text])
        self.callbacks[update.message.from_user.username] = cb

        projects = self._getProjects(username)
        reply_markup = telegram.ReplyKeyboardMarkup([projects], resize_keyboard=True, one_time_keyboard=True, selective=True)
        return bot.sendMessage(chat_id=update.message.chat_id, text="Please enter the name of the project you want to delete", reply_markup=reply_markup)

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
        self.bot.logger.debug('project management for: %s' % username)
        if not self._userCheck(bot, update):
            return

        # no arguments
        if len(args) == 0:
            return self.choose_action(bot, update)

        # projects list
        if args[0] == "list":
            return self.list(bot, update)

        # projects delete
        if (args[0] == "delete" or args[0] == "remove") and len(args) == 1:
            projects = self._getProjects(username)
            return bot.sendMessage(chat_id=update.message.chat_id, text="Ehm, need to give me a project name")

        if (args[0] == "delete" or args[0] == "remove") and len(args) > 1:
            args.pop(0)
            return self.delete(bot, update, args)

        # creating project
        return self.checkout(bot, update, args[0])
