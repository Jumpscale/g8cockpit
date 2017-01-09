from JumpScale import j
import telegram
from .utils import chunks, AYS_REPO_DIR
import time
import os


class BlueprintMgmt(object):

    def __init__(self, bot):
        self.bot = bot
        self.rootpath = bot.rootpath
        self.callbacks = bot.question_callbacks

    # helpers
    def _blueprintsPath(self, repo_name):
        repo = j.atyourservice.repoGet(j.sal.fs.joinPaths(AYS_REPO_DIR, repo_name))
        return '%s/blueprints' % (repo.path)

    def _currentRepoName(self, username):
        return self.bot.repo_mgmt._currentRepoName(username)

    def _currentRepo(self, username):
        return j.atyourservice.repoGet(j.sal.fs.joinPaths(AYS_REPO_DIR, self._currentRepoName(username)))

    def _currentBlueprintsPath(self, username):
        return self._blueprintsPath(self._currentRepoName(username))

    # blueprint management
    def create(self, bot, update, repo):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        if not self._currentRepoName(username):
            message = "No repo selected, you need to select a repo before sending me blueprint. See /repo"
            return self.bot.sendMessage(chat_id=update.message.chat_id, text=message)

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
            j.data.serializer.yaml.loads(update.message.text)
        except Exception as e:
            message = "This is not a valid blueprint. check the syntaxe"
            return self.bot.sendMessage(chat_id=update.message.chat_id, text=message)

        # saving blueprint
        try:
            custom = generate_unique_name()
            bp_dir = self._currentBlueprintsPath(username)
            bp_path = '%s/%s' % (bp_dir, custom)
            j.sal.fs.writeFile(bp_path, update.message.text)
            msg = """Blueprint has been created. To execute blueprint use ;`blueprint execute`"""
            if msg:
                self.bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)
        except Exception as e:
            msg = 'Error during blueprint execution, check validity of your blueprint.\n Error: %s' % str(e)
            return self.bot.sendMessage(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

        evt = j.data.models.cockpit_event.Telegram()
        evt.io = 'input'
        evt.action = 'bp.create'
        evt.args = {
            'username': username,
            'path': bp_dir,
            'content': update.message.text,
        }
        self.bot.send_event(evt.to_json())

    def execute(self, bot, update, blueprint_name):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        # execute blueprint
        msg = 'Start execution of enabled blueprints...'
        self.bot.sendMessage(chat_id=chat_id, text=msg)

        try:
            current_repo = self._currentRepo(username)
            current_repo.blueprintExecute()
        except Exception as e:
            msg = 'Error during blueprint execution, check validity of your blueprint.\n Error: %s' % str(e)
            self.logger.error(e.message)
        else:
            msg = "Blueprint deployed. Run with `/run create` then `/run exec`"

        self.bot.sendMessage(
            chat_id=chat_id,
            text=msg)

    def list(self, bot, update):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        repo = self._currentRepo(username)
        bluelist = [bp.name for bp in repo.blueprints]

        if len(bluelist) <= 0:
            self.bot.sendMessage(
                chat_id=update.message.chat_id,
                text="Sorry, this repository doesn't contains blueprint for now, upload me some of them !")
            return

        def cb(bot, update):
            message = update.message
            if message.text in bluelist:
                bp = repo.blueprintGet(message.text)
                content = bp.content
                text = '```\n%s\n```' % content
                self.bot.sendMessage(
                    chat_id=update.message.chat_id,
                    text=text,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup=telegram.ReplyKeyboardHide())
            else:
                self.bot.sendMessage(
                    chat_id=update.message.chat_id,
                    text="%s is not a valid Blueprint name" %
                    message.text,
                    reply_markup=telegram.ReplyKeyboardHide())
        self.callbacks[username] = cb

        reply_markup = telegram.ReplyKeyboardMarkup(
            list(chunks(bluelist, 4)), resize_keyboard=True, one_time_keyboard=True)
        self.bot.sendMessage(
            chat_id=update.message.chat_id,
            text="Click on the blueprint you want to inspect",
            reply_markup=reply_markup)

    def disable(self, bot, update, blueprint):
        chat_id = update.message.chat_id
        username = update.message.from_user.username
        repo = self._currentRepo(username)
        bp = repo.blueprintGet("%s" % blueprint)

        bp.disable()
        bot.sendMessage(text="blueprint disbaled successfuly",
                        chat_id=chat_id)

    def enable(self, bot, update, blueprint):
        chat_id = update.message.chat_id
        username = update.message.from_user.username
        repo = self._currentRepo(username)
        bp = repo.blueprintGet("_%s" % blueprint)

        bp.enable()
        bot.sendMessage(text="blueprint enabled successfuly",
                        chat_id=chat_id)

    def delete(self, bot, update, names):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        repo = self._currentRepo(username)

        # ays uninstall before
        def delete_bp(path):
            try:
                bp = repo.blueprintGet(path)

                msg = 'Start deletion of blueprint %s' % bp.name
                self.bot.logger.debug(msg)
                self.bot.sendMessage(chat_id=chat_id, text=msg)
                j.sal.fs.remove(bp.path)
                msg = "blueprint %s removed" % (bp.name)

            except Exception as e:
                msg = "Error during deletion of blueprint %s: %s" % (bp.name, str(e))

            finally:
                self.bot.sendMessage(chat_id=update.message.chat_id, text=msg)
                evt = j.data.models.cockpit_event.Telegram()
                evt.io = 'input'
                evt.action = 'bp.delete'
                evt.args = {
                    'username': username,
                    'path': path,
                }
                self.bot.send_event(evt.to_json())

        to_delete = []
        if len(names) == 1 and names[0] in ['*', 'all']:
            blueprint_paths = j.sal.fs.listFilesInDir(self._currentBlueprintsPath(username))
            for path in blueprint_paths:
                to_delete.append(path)
        else:
            for name in names:
                path = j.sal.fs.joinPaths(self._currentBlueprintsPath(username), name)
                if not j.sal.fs.exists(path):
                    continue
                to_delete.append(path)

        for bp in to_delete:
            delete_bp(bp)

    # UI interaction
    def choose_action(self, bot, update):
        self.callbacks[update.message.from_user.username] = self.dispatch_choice
        choices = ['add', 'execute', 'list', 'delete']
        reply_markup = telegram.ReplyKeyboardMarkup([choices], resize_keyboard=True, one_time_keyboard=True)
        return self.bot.sendMessage(chat_id=update.message.chat_id,
                                    text="What do you want to do ?", reply_markup=reply_markup)

    def dispatch_choice(self, bot, update):
        message = update.message
        if message.text == "add":
            self.create_prompt(bot, update)
        elif message.text == 'execute':
            self.execute_prompt(bot, update)
        elif message.text == 'list':
            self.list(bot, update)
        elif message.text == 'delete':
            self.delete_prompt(bot, update)

    def create_prompt(self, bot, update):
        def cb(bot, update):
            self.create(bot, update, update.message.text)
        self.callbacks[update.message.from_user.username] = cb
        return self.bot.sendMessage(chat_id=update.message.chat_id, text="Please paste your blueprint here now.")

    def disable_prompt(self, bot, update):
        username = update.message.from_user.username
        blueprints = j.sal.fs.listFilesInDir(self._currentBlueprintsPath(username))

        bluelist = []

        for bluepath in blueprints:
            blueprint = j.sal.fs.getBaseName(bluepath)
            if not blueprint.startswith("_"):
                bluelist.append(blueprint)

        if len(bluelist) == 0:
            return self.bot.sendMessage(
                chat_id=update.message.chat_id,
                text="Sorry, this repository doesn't contains blueprint for now, upload me some of them !")

        def cb(bot, update):
            self.disable(bot, update, update.message.text)
        self.callbacks[username] = cb

        custom_keyboard = [bluelist]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
        return self.bot.sendMessage(chat_id=update.message.chat_id,
                                    text="Which blueprint do you want to disable ?", reply_markup=reply_markup)

    def enable_prompt(self, bot, update):
        username = update.message.from_user.username
        blueprints = os.listdir(self._currentBlueprintsPath(username))

        bluelist = []

        for bluepath in blueprints:
            blueprint = j.sal.fs.getBaseName(bluepath)
            if blueprint.startswith("_"):
                blueprint = blueprint.replace("_", "")
                bluelist.append(blueprint)

        if len(bluelist) == 0:
            return self.bot.sendMessage(
                chat_id=update.message.chat_id,
                text="Sorry, this repository doesn't contains blueprint for now, upload me some of them !")

        def cb(bot, update):
            self.enable(bot, update, update.message.text)
        self.callbacks[username] = cb

        custom_keyboard = [bluelist]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
        return self.bot.sendMessage(chat_id=update.message.chat_id,
                                    text="Which blueprint do you want to enable ?", reply_markup=reply_markup)

    def execute_prompt(self, bot, update):
        username = update.message.from_user.username
        blueprints = j.sal.fs.listFilesInDir(self._currentBlueprintsPath(username))

        bluelist = []

        for bluepath in blueprints:
            blueprint = j.sal.fs.getBaseName(bluepath)
            bluelist.append(blueprint)

        if len(bluelist) == 0:
            return self.bot.sendMessage(
                chat_id=update.message.chat_id,
                text="Sorry, this repository doesn't contains blueprint for now, upload me some of them !")

        def cb(bot, update):
            self.execute(bot, update, [update.message.text])
        self.callbacks[username] = cb

        custom_keyboard = [bluelist]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
        return self.bot.sendMessage(chat_id=update.message.chat_id,
                                    text="Which blueprint do you want to execute ?", reply_markup=reply_markup)

    def delete_prompt(self, bot, update):
        username = update.message.from_user.username
        blueprints = j.sal.fs.listFilesInDir(self._currentBlueprintsPath(username))

        bluelist = []

        for bluepath in blueprints:
            blueprint = j.sal.fs.getBaseName(bluepath)
            bluelist.append(blueprint)

        if len(bluelist) == 0:
            return self.bot.sendMessage(
                chat_id=update.message.chat_id,
                text="Sorry, this repository doesn't contains blueprint for now, upload me some of them !")

        def cb(bot, update):
            self.delete(bot, update, [update.message.text])
        self.callbacks[username] = cb

        custom_keyboard = [bluelist]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
        return self.bot.sendMessage(chat_id=update.message.chat_id,
                                    text="Which blueprint do you want to delete ?", reply_markup=reply_markup)

    # Handler for robot
    def handler(self, bot, update, args):
        username = update.message.from_user.username

        self.bot.logger.debug('blueprint management for: %s' % username)
        if not self.bot.repo_mgmt._userCheck(bot, update):
            return

        if not self._currentRepoName(username):
            message = "Sorry, you are not working on a repo currently, use `/repo` to select a repository"
            return self.bot.sendMessage(chat_id=update.message.chat_id, text=message,
                                        parse_mode=telegram.ParseMode.MARKDOWN)

        # no arguments
        if len(args) == 0:
            self.choose_action(bot, update)
            return
        else:
            # add blueprints
            if args[0] == "add" or args[0] == 'create':
                return self.create_prompt(bot, update)

            # execute blueprints
            if (args[0] == "execute" or args[0] == "exec") and len(args) == 1:
                return self.execute_prompt(bot, update)

            if (args[0] == "execute" or args[0] == "exec") and len(args) > 1:
                return self.execute(bot, update, args[1])

            # list blueprints
            if args[0] == "list":
                return self.list(bot, update)

            # delete a blueprints
            if (args[0] == "delete" or args[0] == "remove") and len(args) == 1:
                return self.delete_prompt(bot, update)

            if (args[0] == "delete" or args[0] == "remove") and len(args) > 1:
                args.pop(0)
                return self.delete(bot, update, args)

            # enable blueprint
            if args[0] == "enable" and len(args) == 1:
                return self.enable_prompt(bot, update)

            if args[0] == "enable" and len(args) > 1:
                args.pop(0)
                return self.enable(bot, update, args)

            # disable blueprint
            if args[0] == "disbale" and len(args) == 1:
                return self.disable_prompt(bot, update)

            if args[0] == "disable" and len(args) > 1:
                args.pop(0)
                return self.disable(bot, update, args)

    def document(self, bot, update):
        username = update.message.from_user.username
        doc = update.message.document
        item = bot.getFile(doc.file_id)
        local = '%s/%s' % (self._currentBlueprintsPath(username), doc.file_name)

        if not self._currentRepoName(username):
            message = "Sorry, you are not working on a repo currently, use `/repo` to select a repository"
            return self.bot.sendMessage(chat_id=update.message.chat_id, text=message,
                                        parse_mode=telegram.ParseMode.MARKDOWN)

        if j.sal.fs.exists(local):
            j.sal.fs.remove(local)

        self.bot.logger.debug("document: %s -> %s" % (item.file_path, local))
        j.sal.nettools.download(item.file_path, local)

        self.bot.sendMessage(chat_id=update.message.chat_id, text="File received: %s" % doc.file_name)
