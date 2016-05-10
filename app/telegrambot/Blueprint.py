from JumpScale import j
import telegram
from .utils import chunks

class BlueprintMgmt(object):

    def __init__(self, bot):
        self.bot = bot
        self.rootpath = bot.rootpath
        self.callbacks = bot.question_callbacks

    #helpers
    def _blueprintsPath(self, repo_name):
        repo = j.atyourservice.get(name=repo_name)
        return '%s/blueprints' % (repo.basepath)

    def _currentRepo(self, username):
        return self.bot.repo_mgmt._currentRepo(username)

    def _currentRepoPath(self, username):
        repo = j.atyourservice.get(name=self._currentRepo(username))
        return repo.basepath

    def _currentBlueprintsPath(self, username):
        return self._blueprintsPath(self._currentRepo(username))

    # blueprint management
    def create(self, bot, update, repo):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        if not self._currentRepo(username):
            message = "No repo selected, you need to select a repo before sending me blueprint. See /repo"
            return bot.sendMessage(chat_id=update.message.chat_id, text=message)

        def generate_unique_name():
            name = '%s.yaml' % j.data.time.getLocalTimeHRForFilesystem()
            path = '%s/%s' % (self._currentBlueprintsPath(username), name)
            while j.sal.fs.exists(path):
                time.sleep(1)
                name = '%s.yaml' % j.data.time.getLocalTimeHRForFilesystem()
                path = '%s/%s' % (self._currentBlueprintsPath(username), name)
            return name

        # check if it's a blueprint
        try:
            yaml = j.data.serializer.yaml.loads(update.message.text)
        except e:
            message = "This is not a valid blueprint. check the syntaxe"
            return bot.sendMessage(chat_id=update.message.chat_id, text=message)

        # saving blueprint
        try:
            custom = generate_unique_name()
            bp_dir = self._currentBlueprintsPath(username)
            bp_path = '%s/%s' % (bp_dir, custom)
            j.sal.fs.writeFile(bp_path, update.message.text)

            # execute blueprint
            repo = j.atyourservice.get(name=self._currentRepo(username))
            bp = repo.getBlueprint(bp_path)

            msg = 'Start execution of your blueprint...'
            bot.sendMessage(chat_id=chat_id, text=msg)

            bp.load()
            repo.init()

            message = "Blueprint deployed. Check your service with `/service list`"
            bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
        except Exception as e:
            j.sal.fs.remove(bp_path)
            msg = 'Error during blueprint execution, check validity of your blueprint'
            return bot.sendMessage(chat_id=chat_id, text=msg)

        evt = j.data.models.cockpit_event.Telegram()
        evt.io = 'input'
        evt.action = 'bp.create'
        evt.args = {
            'username': username,
            'path': bp_dir,
            'content': update.message.text,
        }
        self.bot.send_event(evt.to_json())

    def list(self, bot, update):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        blueprint_path = self._currentBlueprintsPath(username)
        blueprints = j.sal.fs.listFilesInDir(blueprint_path)

        bluelist = []
        for bluepath in blueprints:
            blueprint = j.sal.fs.getBaseName(bluepath)
            bluelist.append(blueprint)

        if len(bluelist) <= 0:
            bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, this repository doesn't contains blueprint for now, upload me some of them !")
            return

        def cb(bot, update):
            message = update.message
            if message.text in bluelist:
                content = j.sal.fs.fileGetContents(j.sal.fs.joinPaths(blueprint_path, message.text))
                text = '```\n%s\n```' % content
                bot.sendMessage(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=telegram.ReplyKeyboardHide())
            else:
                bot.sendMessage(chat_id=update.message.chat_id, text="%s is not a valid Blueprint name" % message.text, reply_markup=telegram.ReplyKeyboardHide())
        self.callbacks[username] = cb

        reply_markup = telegram.ReplyKeyboardMarkup(list(chunks(bluelist, 4)), resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id, text="Click on the blueprint you want to inspect", reply_markup=reply_markup)

    def delete(self, bot, update, repo, names):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        # ays uninstall before
        # self._ays_sync(bot, update, args=['do', 'uninstall'])
        # j.actions.resetAll()
        def delete_bp(path):
            j.sal.fs.remove(blueprint)
            evt = j.data.models.cockpit_event.Telegram()
            evt.io = 'input'
            evt.action = 'bp.delete'
            evt.args = {
                'username': username,
                'path': path,
            }
            self.bot.send_event(evt.to_json())

        for name in names:
            if name == "*" or name == "all":
                blueprints = j.sal.fs.listFilesInDir(self._currentBlueprintsPath(username))
                for blueprint in blueprints:
                    delete_bp(blueprint)

                ln = len(blueprints)
                message = "%d blueprint%s removed" % (ln, "s" if ln > 1 else "")
                bot.sendMessage(chat_id=update.message.chat_id, text=message)

            else:
                blueprint = '%s/%s' % (self._blueprintsPath(repo), name)

                self.bot.logger.debug('deleting: %s' % blueprint)

                if not j.sal.fs.exists(blueprint):
                    message = "Sorry, I don't find any blueprint named `%s`, you can list them with `/blueprint`" % name
                    bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
                    continue

                delete_bp(blueprint)

                message = "Blueprint `%s` removed from `%s`" % (name, repo)
                bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

        # cleaning
        j.sal.fs.removeDirTree('%s/alog' % self._currentRepoPath(username))
        j.sal.fs.removeDirTree('%s/recipes' % self._currentRepoPath(username))
        j.sal.fs.removeDirTree('%s/services' % self._currentRepoPath(username))
        j.sal.fs.createDir('%s/services' % self._currentRepoPath(username))

    # UI interaction
    def choose_action(self, bot, update):
        self.callbacks[update.message.from_user.username] = self.dispatch_choice
        choices = ['add', 'list', 'delete']
        reply_markup = telegram.ReplyKeyboardMarkup([choices], resize_keyboard=True, one_time_keyboard=True)
        return bot.sendMessage(chat_id=update.message.chat_id, text="What do you want to do ?", reply_markup=reply_markup)

    def dispatch_choice(self, bot, update):
        message = update.message
        username = update.message.from_user.username
        repo = self._currentRepo(username)
        if message.text == "add":
            self.create_prompt(bot, update)
        elif message.text == 'list':
            self.list(bot, update)
        elif message.text == 'delete':
            self.delete_prompt(bot, update)

    def create_prompt(self, bot, update):
        def cb(bot, update):
            self.create(bot, update, update.message.text)
        self.callbacks[update.message.from_user.username] = cb
        return bot.sendMessage(chat_id=update.message.chat_id, text="Please paste your blueprint here now.")

    def delete_prompt(self, bot, update):
        username = update.message.from_user.username
        blueprints = j.sal.fs.listFilesInDir(self._currentBlueprintsPath(username))

        bluelist = []

        for bluepath in blueprints:
            blueprint = j.sal.fs.getBaseName(bluepath)
            bluelist.append(blueprint)

        if len(bluelist) == 0:
            return bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, this repository doesn't contains blueprint for now, upload me some of them !")

        def cb(bot, update):
            self.delete(bot, update, self._currentRepo(username), [update.message.text])
        self.callbacks[username] = cb

        custom_keyboard = [bluelist]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
        return bot.sendMessage(chat_id=update.message.chat_id, text="Which blueprint do you want to delete ?", reply_markup=reply_markup)

    # Handler for robot
    def handler(self, bot, update, args):
        username = update.message.from_user.username

        self.bot.logger.debug('blueprint management for: %s' % username)
        if not self.bot.repo_mgmt._userCheck(bot, update):
            return

        if not self._currentRepo(username):
            message = "Sorry, you are not working on a repo currently, use `/repo [name]` to create a new one"
            return bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

        # no arguments
        if len(args) == 0:
            self.choose_action(bot, update)
            return
        else:
            # add blueprints
            if args[0] == "add" or args[0] == 'create':
                return self.create_prompt(bot, update)

            # list blueprints
            if args[0] == "list":
                return self.list(bot, update)

            # delete a blueprints
            if (args[0] == "delete" or args[0] == "remove") and len(args) == 1:
                return self.delete_prompt(bot, update, self._currentRepo(username))

            if (args[0] == "delete" or args[0] == "remove") and len(args) > 1:
                args.pop(0)
                return self.delete(bot, update, self._currentRepo(username), args)

    def document(self, bot, update):
        username = update.message.from_user.username
        doc = update.message.document
        item = bot.getFile(doc.file_id)
        local = '%s/%s' % (self._currentBlueprintsPath(username), doc.file_name)

        if not self._currentRepo(username):
            message = "Sorry, you are not working on a repo currently, use `/repo [name]` to create a new one"
            return bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

        if j.sal.fs.exists(local):
            j.sal.fs.remove(local)

        self.bot.logger.debug("document: %s -> %s" % (item.file_path, local))
        j.sal.nettools.download(item.file_path, local)

        bot.sendMessage(chat_id=update.message.chat_id, text="File received: %s" % doc.file_name)
