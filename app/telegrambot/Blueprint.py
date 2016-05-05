from JumpScale import j
import telegram


class BlueprintMgmt(object):

    def __init__(self, bot):
        self.bot = bot
        self.rootpath = bot.rootpath
        self.callbacks = bot.question_callbacks

    #helpers
    def _blueprintsPath(self, username, project):
        return '%s/%s/%s/blueprints' % (self.rootpath, username, project)

    def _currentProject(self, username):
        return self.bot.project_mgmt._currentProject(username)

    def _currentProjectPath(self, username):
        return self.bot.project_mgmt._projectPath(username, self.bot.project_mgmt._currentProject(username))

    def _currentBlueprintsPath(self, username):
        return self._blueprintsPath(username, self.bot.project_mgmt._currentProject(username))

    # def _blueprintGetAll(self, bot, update, project):
    #     files = j.sal.fs.listFilesInDir(self._blueprintsPath(username, project))
    #     print("blueprints: %s" % files)
    #
    #     for file in files:
    #         name = j.sal.fs.getBaseName(file)
    #         self._blueprintGet(bot, update, name, project)
    #
    # def _blueprintGet(self, bot, update, name, project):
    #     username = update.message.from_user.username
    #     blueprint = '%s/%s' % (self._blueprintsPath(username, project), name)
    #
    #     print('grabbing: %s' % blueprint)
    #
    #     if not j.sal.fs.exists(blueprint):
    #         message = "Sorry, I don't find this blueprint, you can list them with `/blueprint`"
    #         return bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode="Markdown")
    #
    #     content = j.sal.fs.fileGetContents(blueprint)
    #     self.bulkSend(bot, update, content)

    # blueprint management
    def create(self, bot, update, project):
        username = update.message.from_user.username
        if not self._currentProject(username):
            message = "No project selected, you need to select a project before sending me blueprint. See /project"
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
        custom = generate_unique_name()
        local = '%s/%s' % (self._currentBlueprintsPath(username), custom)
        j.sal.fs.writeFile(local, update.message.text)

        evt = j.data.models.cockpit_event.Telegram()
        evt.io = 'input'
        evt.action = 'bp.create'
        evt.args = {
            'username': username,
            'path': local,
            'content': update.message.text,
        }
        self.bot.send_event(evt.to_json())

        message = "This look like a blueprint, I saved it to: %s" % local
        bot.sendMessage(chat_id=update.message.chat_id, text=message)

    def list(self, bot, update, project):
        username = update.message.from_user.username
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

        reply_markup = telegram.ReplyKeyboardMarkup([bluelist])
        bot.sendMessage(chat_id=update.message.chat_id, text="Click on the blueprint you want to inspect", reply_markup=reply_markup)

    def delete(self, bot, update, project, names):
        username = update.message.from_user.username

        # ays uninstall before
        # self._ays_sync(bot, update, args=['do', 'uninstall'])
        # j.actions.resetAll()
        def delete_bp(path):
            j.sal.fs.remove(blueprint)
            evt = j.data.models.cockpit_event.Telegram()
            evt.io = 'input'
            evt.action = 'bp.create'
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
                blueprint = '%s/%s' % (self._blueprintsPath(username, project), name)

                self.bot.logger.debug('deleting: %s' % blueprint)

                if not j.sal.fs.exists(blueprint):
                    message = "Sorry, I don't find any blueprint named `%s`, you can list them with `/blueprint`" % name
                    bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode="Markdown")
                    continue

                delete_bp(blueprint)

                message = "Blueprint `%s` removed from `%s`" % (name, project)
                bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode="Markdown")

        # cleaning
        j.sal.fs.removeDirTree('%s/alog' % self._currentProjectPath(username))
        j.sal.fs.removeDirTree('%s/recipes' % self._currentProjectPath(username))
        j.sal.fs.removeDirTree('%s/services' % self._currentProjectPath(username))
        j.sal.fs.createDir('%s/services' % self._currentProjectPath(username))

    # UI interaction
    def choose_action(self, bot, update):
        self.callbacks[update.message.from_user.username] = self.dispatch_choice
        choices = ['add', 'list', 'delete']
        reply_markup = telegram.ReplyKeyboardMarkup([choices], resize_keyboard=True, one_time_keyboard=True)
        return bot.sendMessage(chat_id=update.message.chat_id, text="What do you want to do ?", reply_markup=reply_markup)

    def dispatch_choice(self, bot, update):
        message = update.message
        username = update.message.from_user.username
        project = self._currentProject(username)
        if message.text == "add":
            self.create_prompt(bot, update)
        elif message.text == 'list':
            self.list(bot, update, project)
        elif message.text == 'delete':
            self.delete_prompt(bot, update, project)

    def create_prompt(self, bot, update):
        def cb(bot, update):
            self.create(bot, update, update.message.text)
        self.callbacks[update.message.from_user.username] = cb
        return bot.sendMessage(chat_id=update.message.chat_id, text="Please paste your blueprint here now.")

    def delete_prompt(self, bot, update, project):
        username = update.message.from_user.username
        blueprints = j.sal.fs.listFilesInDir(self._currentBlueprintsPath(username))

        bluelist = []

        for bluepath in blueprints:
            blueprint = j.sal.fs.getBaseName(bluepath)
            bluelist.append(blueprint)

        if len(bluelist) == 0:
            return bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, this repository doesn't contains blueprint for now, upload me some of them !")

        def cb(bot, update):
            self.delete(bot, update, self._currentProject(username), [update.message.text])
        self.callbacks[username] = cb

        custom_keyboard = [bluelist]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
        return bot.sendMessage(chat_id=update.message.chat_id, text="Which blueprint do you want to delete ?", reply_markup=reply_markup)

    # Handler for robot
    def handler(self, bot, update, args):
        username = update.message.from_user.username

        self.bot.logger.debug('blueprint management for: %s' % username)
        if not self.bot.project_mgmt._userCheck(bot, update):
            return

        if not self._currentProject(username):
            message = "Sorry, you are not working on a project currently, use `/project [name]` to create a new one"
            return bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode="Markdown")

        # no arguments
        if len(args) == 0:
            self.choose_action(bot, update)
            return
            # return self.list(bot, update, self._currentProject(username))

        # list blueprints
        if args[0] == "list":
            return self.list(bot, update, self._currentProject(username))

        # delete a blueprints
        if (args[0] == "delete" or args[0] == "remove") and len(args) == 1:
            return self.delete_prompt(bot, update, self._currentProject(username))

        if (args[0] == "delete" or args[0] == "remove") and len(args) > 1:
            args.pop(0)
            return self.delete(bot, update, self._currentProject(username), args)

        if args[0] == "all":
            return self._blueprintGetAll(bot, update, self._currentProject(username))

        # retreive blueprint
        return self._blueprintGet(bot, update, args[0], self._currentProject(username))

    def document(self, bot, update):
        username = update.message.from_user.username
        doc = update.message.document
        item = bot.getFile(doc.file_id)
        local = '%s/%s' % (self._currentBlueprintsPath(username), doc.file_name)

        if not self._currentProject(username):
            message = "Sorry, you are not working on a project currently, use `/project [name]` to create a new one"
            return bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode="Markdown")

        if j.sal.fs.exists(local):
            j.sal.fs.remove(local)

        self.bot.logger.debug("document: %s -> %s" % (item.file_path, local))
        j.sal.nettools.download(item.file_path, local)

        bot.sendMessage(chat_id=update.message.chat_id, text="File received: %s" % doc.file_name)
