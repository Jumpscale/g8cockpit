from JumpScale import j
import telegram
from .utils import chunks
# from JumpScale.baselib.atyourservice.robot.ActionRequest import *

class ServiceMgmt(object):

    def __init__(self, bot):
        self.bot = bot
        self.rootpath = bot.rootpath
        self.callbacks = bot.question_callbacks

    #helpers
    def _blueprintsPath(self, repo):
        return '%s/%s/%s/blueprints' % (self.rootpath, repo)

    def _currentRepo(self, username):
        return self.bot.repo_mgmt._currentRepo(username)

    def _currentRepoPath(self, username):
        repo = j.atyourservice.get(name=self._currentRepo(username))
        return repo.basepath

    def _currentBlueprintsPath(self, username):
        return self._blueprintsPath(self._currentRepo(username))

    def execute(self, bot, update, action, role='', instance=''):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        evt = j.data.models.cockpit_event.Telegram()
        evt.io = 'input'
        evt.action = 'service.execute'
        evt.args = {
            'username': username,
            'chat_id': update.message.chat_id,
            'role': role,
            'instance': instance,
            'action': action,
            'repo': self._currentRepoPath(username),
            'notify': True
        }
        self.bot.send_event(evt.to_json())

    def list(self, bot, update, repo_name):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        repo = j.atyourservice.get(name=repo_name)

        if len(repo.services) <= 0:
            bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, this repository doesn't contains services for now.")
            return

        services_list = []
        for service in repo.services.keys():
            services_list.append('- %s' % service.replace("_", "\_"))

        msg = '\n'.join(services_list)
        bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

    def inspect(self, bot, update, services):
        for service in services:
            msg = """Role: *{role}*
Instances: *{instance}*
HRD:
`{hrd}`
State:
```
 {state}
```
""".format(role=service.role, instance=service.instance, hrd=str(service.hrd), state=str(service.state))
            bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=telegram.ReplyKeyboardHide())

    def delete(self, bot, update, repo, names):
        username = update.message.from_user.username
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        raise NotImplemented("Deleting service is not supported yet")

    # UI interaction
    def choose_action(self, bot, update):
        self.callbacks[update.message.from_user.username] = self.dispatch_choice
        choices = ['list', 'inspect', 'execute']
        reply_markup = telegram.ReplyKeyboardMarkup([choices], resize_keyboard=True, one_time_keyboard=True)
        return bot.sendMessage(chat_id=update.message.chat_id, text="What do you want to do ?", reply_markup=reply_markup)

    def dispatch_choice(self, bot, update):
        message = update.message
        username = update.message.from_user.username
        repo = self._currentRepo(username)
        if message.text == 'list':
            self.list(bot, update, repo)
        elif message.text in ['execute', 'exec']:
            self.execute_prompt(bot, update)
        elif message.text in ['inspect', 'see']:
            self.inspect_prompt(bot, update)

    def execute_prompt(self, bot, update):
        username = update.message.from_user.username

        def select_action(bot, update):
            domain, name, instance, role = j.atyourservice._parseKey(update.message.text)
            services = repo.findServices(instance=instance, role=role)

            def execute(bot, update):
                action_name = update.message.text
                self.execute(bot, update, action_name, role, instance)
            actions = set()
            for s in services:
                for action_name in list(s.action_methods.keys()):
                    actions.add(action_name)

            actions = list(actions)
            actions.sort()
            keys = list(chunks(actions, 4))
            reply_markup = telegram.ReplyKeyboardMarkup(keys, resize_keyboard=True, one_time_keyboard=True)
            msg = 'Select the action you want to execute'
            bot.sendMessage(chat_id=update.message.chat_id, text=msg, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
            self.callbacks[username] = execute

        self.callbacks[username] = select_action
        repo = j.atyourservice.get(name=self._currentRepo(username))
        services = list(repo.services.keys())
        services.sort()
        if len(repo.services) <= 0:
            msg = "There is not service instance in this repo yet. Deploy a blueprint to create service instances"
            return bot.sendMessage(chat_id=update.message.chat_id, text=msg)

        reply_markup = telegram.ReplyKeyboardMarkup(list(chunks(services, 4)), resize_keyboard=True, one_time_keyboard=True)
        msg = """
        Choose a service to execution action on or type a key to match multiple service.
        example :
        `@node` to match all service with role node
        `node!bot` to match the service with role node and instance name bot.
        """
        return bot.sendMessage(chat_id=update.message.chat_id, text=msg, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)

    def inspect_prompt(self, bot, update):
        username = update.message.from_user.username

        repo = j.atyourservice.get(name=self._currentRepo(username))
        services = list(repo.services.keys())
        services.sort()
        if len(repo.services) <= 0:
            msg = "There is not service instance in this repo yet. Deploy a blueprint to create service instances"
            return bot.sendMessage(chat_id=update.message.chat_id, text=msg)

        def select_service(bot, update):
            domain, name, instance, role = j.atyourservice._parseKey(update.message.text)
            services = repo.findServices(instance=instance, role=role)
            self.inspect(bot, update, services)

        self.callbacks[username] = select_service
        reply_markup = telegram.ReplyKeyboardMarkup(list(chunks(services, 4)), resize_keyboard=True, one_time_keyboard=True)
        msg = """
        Choose a service to inspect or type a service key to match multiple service.
        example :
        `@node` to match all service with role node
        `node!bot` to match the service with role node and instance name bot.
        """
        return bot.sendMessage(chat_id=update.message.chat_id, text=msg, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)

    def delete_prompt(self, bot, update, repo):
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

        self.bot.logger.debug('service management for: %s' % username)
        if not self.bot.repo_mgmt._userCheck(bot, update):
            return

        if not self._currentRepo(username):
            message = "Sorry, you are not working on a repo currently, use `/repo [name]` to create or select one"
            return bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode="Markdown")

        # no arguments
        if len(args) == 0:
            self.choose_action(bot, update)
            return

        # list services
        if args[0] == "list":
            return self.list(bot, update, self._currentRepo(username))
        # execute action on services
        if args[0] in ["execute", "exec"]:
            if len(args) == 1:
                return self.execute_prompt(bot, update)
            elif len(args) >= 3:
                return self.execute(bot, update, args[1], args[2])
        if args[0] in ['inspect', 'see']:
            if len(args) == 1:
                return self.inspect_prompt(bot, update)
            elif len(args) >= 2:
                return self.inspect(bot, update, args[1])

    def document(self, bot, update):
        username = update.message.from_user.username
        doc = update.message.document
        item = bot.getFile(doc.file_id)
        local = '%s/%s' % (self._currentBlueprintsPath(username), doc.file_name)

        if not self._currentRepo(username):
            message = "Sorry, you are not working on a repo currently, use `/repo [name]` to create a new one"
            return bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode="Markdown")

        if j.sal.fs.exists(local):
            j.sal.fs.remove(local)

        self.bot.logger.debug("document: %s -> %s" % (item.file_path, local))
        j.sal.nettools.download(item.file_path, local)

        bot.sendMessage(chat_id=update.message.chat_id, text="File received: %s" % doc.file_name)
