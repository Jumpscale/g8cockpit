import telegram
import queue
from JumpScale import j

class TelegramAsker(object):
    """Asker Interface with telegram"""
    # TODO implement retry on ask* Methods

    def __init__(self, updater, chat_id, username):
        """
        Updater is the telegram.ext.update object from telegram library
        """
        super(TelegramAsker, self).__init__()
        self.chat_id = chat_id
        self.username = username
        self.updater = updater
        self.bot = self.updater.bot
        self.queue = queue.Queue(maxsize=1)
        self.question_tmpl = """
*QUESTION :*
{message}
"""
        self.g8_choices = []

    def say(self, msg):
        self.bot.sendMessage(chat_id=self.chat_id, text=msg)

    def askYesNo(self, message):
        custom_keyboar = [['yes', 'no']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboar, resize_keyboard=True, one_time_keyboard=True)

        message = self.question_tmpl.format(message=message)
        message = self.bot.sendMessage(chat_id=self.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)
        value = self.queue.get()
        return value

    def askChoice(self, message, choices):
        custom_keyboar = []
        for i in range(0, len(choices), 2):
            custom_keyboar.append(choices[i:i+2])
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboar, resize_keyboard=True, one_time_keyboard=True)
        message = self.question_tmpl.format(message=message)
        message = self.bot.sendMessage(chat_id=self.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)
        value = self.queue.get()
        return value

    def askString(self, message, default=None):
        reply_markup = telegram.ForceReply()
        message = self.question_tmpl.format(message=message)
        message = self.bot.sendMessage(chat_id=self.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)
        value = self.queue.get()
        return value

    def ask_repo_url(self):
        repo_url = self.askString("Please enter the url of the git repository where to store the ays repo of your cockpit. The repo need to exists")
        return repo_url

    def ask_ovc_url(self):
        def validate(input):
            return j.sal.nettools.checkUrlReachable(input)
        ovc_url = self.askChoice("Please enter the url of the G8 where to deploy your cockpit.", choices=self.g8_choices)
        return ovc_url

    def ask_ovc_login(self):
        def validate(input):
            return True
        login = self.askString("Please enter the login of your account on the G8 where to deploy the cockpit")
        return login

    def ask_ovc_password(self):
        def validate(input):
            return True
        passwd = self.askString("Please enter the password of your account on the G8 where to deploy cockpit")
        return passwd

    def ask_ovc_vdc(self):
        def validate(input):
            return True
        name = self.askChoice("Please select the name of the virtual data center where to deploy the G8 Cockpit", choices=['default', 'cockpit'])
        return name

    def ask_ovc_account(self, ovc_client=None):
        """
        ovc_client: if ovc client is given.
            first check if only one account is available, if so don't ask anything and just return the account
            If multiple account, ask with proposition.
            If no ovc_client, accept any entry
        """
        if ovc_client:
            if len(ovc_client.accounts) == 1:
                account = ovc_client.accounts[0]
                accoutn_name = account.model['name']
            elif len(ovc_client.accounts) > 1:
                choices = [acc.model['name'] for acc in ovc_client.accounts]
                accoutn_name = self.askChoice('Choose which account to use', choices)
            return accoutn_name

        # if not ovc_client or accounts number is 0
        def validate(input):
            return True
        accoutn_name = self.askString("Account to use on the G8 wherre to deploy the cockpit")
        return accoutn_name

    def ask_ovc_location(self, ovc_client=None, account_name=None, vdc_name=None):
        """
        ovc_client: if ovc client is given.
            first check if only one location is available, if so don't ask anything and just return the location
            If multiple location,
                if accoutn_name and vdc_name are given, automaticly retrieve location base on the name of the vdc
                if not account_name and vdc_name, ask to choose between all available locations
            If no ovc_client, accept any entry
        """
        if ovc_client:
            if len(ovc_client.locations) == 1:
                return ovc_client.locations[0]['name']
            elif account_name and vdc_name:
                if account_name in ovc_client.accounts:
                    account = ovc_client.accounts[account_name]
                    if vdc_name in account.spaces:
                        return account.spaces[vdc_name].model['location']
            elif len(ovc_client.locations) > 1:
                choices = [loc.model['name'] for loc in ovc_client.locations]
                location = self.askChoice('Choose which location to use', choices)
                return location

        # if not ovc_client or locations number is 0
        def validate(input):
            return True
        location = self.askString("Location of the vdc choosen")
        return location

    def ask_domain(self):
        def validate(input):
            return True
        domain = self.askChoice("Please choose the domain you want to use for your cockpit", choices=[self.username])
        return domain

    def ask_ssh_key(self):
        def validate(input):
            key = j.do.getSSHKeyFromAgentPub(input, die=False)
            return (key is not None)
        key = self.askString("Please paste the ssh public key you want to authorize in your cockpit")
        return key

    def ask_portal_password(self):
        def validate(input):
            if len(input) < 6:
                return False
            return True
        passwd = self.askString("Admin password for the portal (6 characters minumum)")
        return passwd

    def ask_expose_ssh(self):
        return self.askYesNo("Do you want to expose SSH over http using shellinabox")

    def ask_bot_token(self):
        def validate(input):
            return True
        msg = """
"AtYourService Robot creation
"Please connect to telegram and talk to @botfather.
"execute the command /newbot and choose a name and username for your bot
"@botfather should give you a token, paste it here please :
"""
        token = self.askString(msg)
        return token

    def ask_gid(self):
        def validate(input):
            return j.data.types.int.check(input)
        gid = self.askChoice("Please select a grid ID to give to the controller.", choices=[1, 10, 100])
        return int(gid)

    def ask_organization(self):
        def validate(input):
            return True
        organization = self.askString("Please enter the name of organization you are deploying the cockpit for")
        return organization
