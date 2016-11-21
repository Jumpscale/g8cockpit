from JumpScale import j
import telegram
import re
from .utils import chunks
from telegrambot.Repo import AYS_REPO_DIR
# from JumpScale.baselib.atyourservice.robot.ActionRequest import *


class ServiceMgmt(object):

    def __init__(self, bot):
        self.bot = bot
        self.rootpath = bot.rootpath
        self.callbacks = bot.question_callbacks

    # helpers

    def _currentRepoName(self, username):
        return self.bot.repo_mgmt._currentRepoName(username)

    def _servicelist(self, repo):
        services_list = []
        for service in repo.servicesFind():
            services_list.append('- %s __ %s  =      %s' % (service.model.role,
                                                            service.model.name,
                                                            service.model.key))
        return services_list

    def _currentRepo(self, username):
        return j.atyourservice.repoGet(j.sal.fs.joinPaths(AYS_REPO_DIR, self._currentRepoName(username)))


    def list(self, bot, update, repo_name):
        chat_id = update.message.chat_id
        bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        repo = j.atyourservice.repoGet(j.sal.fs.joinPaths(AYS_REPO_DIR, repo_name))

        if len(repo.services) <= 0:
            self.bot.sendMessage(chat_id=update.message.chat_id,
                                 text="Sorry, this repository doesn't contains services for now.")
            return

        services_list = self._servicelist(repo)

        msg = '\n'.join(services_list).replace("_", "\_")
        self.bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

    def inspect(self, bot, update, service_id):
        username = update.message.from_user.username
        repo = self._currentRepo(username)
        service = repo.serviceGetByKey(service_id).model
        msg = """Role: *{role}*
Instances: *{instance}*
HRD:
`{hrd}`
State:
```
{state}
```
""".format(role=service.role,
           instance=service.name,
           hrd=str(service.dataJSON),
           state=str(service.dictFiltered['state']))
        self.bot.sendMessage(
            chat_id=update.message.chat_id,
            text=msg,
            parse_mode=telegram.ParseMode.MARKDOWN,
            reply_markup=telegram.ReplyKeyboardHide())

    def delete(self, bot, update, service_id):
        username = update.message.from_user.username
        repo = self._currentRepo(username)
        service = repo.serviceGetByKey(service_id).model
        try:
            service.delete()
            chat_id = update.message.chat_id
            msg = "serice hase been deleted successfully"
        except Exception as e:
            self.bot.logger("an Error occured during delete of service : %s" % str(e))
            msg = "serice failed to deleted, service might be in use.\n if error presists please contact our support team."
        bot.sendMessage(text=msg,
                        chat_id=chat_id)

    def choose_action(self, bot, update):
        self.callbacks[update.message.from_user.username] = self.dispatch_choice
        choices = ['list', 'inspect', 'execute']
        reply_markup = telegram.ReplyKeyboardMarkup([choices], resize_keyboard=True, one_time_keyboard=True)
        return self.bot.sendMessage(chat_id=update.message.chat_id,
                                    text="What do you want to do ?", reply_markup=reply_markup)

    def dispatch_choice(self, bot, update):
        message = update.message
        username = update.message.from_user.username
        repo = self._currentRepoName(username)
        if message.text == 'list':
            self.list(bot, update, repo)
        elif message.text in ['delete', 'del']:
            self.delete_prompt(bot, update)
        elif message.text in ['inspect', 'see', 'show']:
            self.inspect_prompt(bot, update)

    def inspect_prompt(self, bot, update):
        username = update.message.from_user.username

        repo = self._currentRepo(username)
        services = self._servicelist(repo)
        if len(repo.services) <= 0:
            msg = "There is not service instance in this repo yet. Deploy a blueprint to create service instances"
            return self.bot.sendMessage(chat_id=update.message.chat_id, text=msg)

        def select_service(bot, update):
            service_id = re.findall("=\W+(\S+)", update.message.text)[0]
            service = repo.serviceGetByKey(service_id)
            self.inspect(bot, update, service)

        self.callbacks[username] = select_service
        reply_markup = telegram.ReplyKeyboardMarkup(
            list(chunks(services, 4)), resize_keyboard=True, one_time_keyboard=True)
        msg = """
        Choose a service to inspect or type a service key to match multiple service.
        """
        return self.bot.sendMessage(chat_id=update.message.chat_id, text=msg,
                                    reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)

    def delete_prompt(self, bot, update):
        username = update.message.from_user.username

        repo = self._currentRepo(username)
        services = self._servicelist(repo)
        if len(repo.services) <= 0:
            msg = "There is not service instance in this repo yet. Deploy a blueprint to create service instances"
            return self.bot.sendMessage(chat_id=update.message.chat_id, text=msg)

        def select_service(bot, update):
            service_id = re.findall("=\W+(\S+)", update.message.text)[0]
            self.delete(bot, update, service_id)

        self.callbacks[username] = select_service
        reply_markup = telegram.ReplyKeyboardMarkup(
            list(chunks(services, 4)), resize_keyboard=True, one_time_keyboard=True)
        msg = """
        Choose a service to inspect or type a service key to match multiple service.
        """
        return self.bot.sendMessage(chat_id=update.message.chat_id, text=msg,
                                    reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)

    # Handler for robot
    def handler(self, bot, update, args):
        username = update.message.from_user.username

        self.bot.logger.debug('service management for: %s' % username)
        if not self.bot.repo_mgmt._userCheck(bot, update):
            return

        if not self._currentRepoName(username):
            message = "Sorry, you are not working on a repo currently, use `/repo` to select a repository"
            return self.bot.sendMessage(chat_id=update.message.chat_id, text=message, parse_mode="Markdown")

        # no arguments
        if len(args) == 0:
            self.choose_action(bot, update)
            return

        # list services
        if args[0] == "list":
            return self.list(bot, update, self._currentRepoName(username))
        # execute action on services
        if args[0] in ["delete", "del"]:
            if len(args) == 1:
                return self.delete_prompt(bot, update)
            elif len(args) >= 3:
                return self.delete(bot, update, args[1])
        if args[0] in ['inspect', 'see', 'show']:
            if len(args) == 1:
                return self.inspect_prompt(bot, update)
            elif len(args) >= 2:
                return self.inspect(bot, update, args[1])
