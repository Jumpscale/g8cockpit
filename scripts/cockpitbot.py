#!/usr/local/bin/jspython

from JumpScale import j

import click

import telegram
from telegram import Updater
from telegram.dispatcher import run_async

# import logging
# logging.basicConfig(level=logging.DEBUG, format='[+][%(levelname)s] %(name)s: %(message)s')

@click.command()
@click.option('--token', '-t', help='Token for the bot')
def cli(token):
        bot = CockpitDeployerBot(token=token)
        bot.run()

class CockpitDeployerBot:
    """docstring for """
    def __init__(self, token):
        self.token = token

        print("[+] initializing cockpit deployer bot")
        self.updater = Updater(token=self.token)
        self.bot = self.updater.bot
        self.deployer = j.clients.cockpit.installer.getBot(self.updater)

        self._register_handlers()

        self.chat_id = None


    def _register_handlers(self):
        dispatcher = self.updater.dispatcher
        dispatcher.addTelegramCommandHandler('start', self.start)
        dispatcher.addUnknownTelegramCommandHandler(self.unknown)

    @run_async
    def start(self, bot, update, **kwargs):
        self.chat_id = update.message.chat_id
        self.deployer.args.asker.chat_id = self.chat_id # TODO better way to set chat it in asker

        username = update.message.from_user.username

        print("[+] hello from: %s (%s %s) [ID %s]" %
              (username,
               update.message.from_user.first_name,
               update.message.from_user.last_name,
               update.message.chat_id))

        hello = "Hello %s !\n" % update.message.from_user.first_name
        self.bot.sendMessage(chat_id=update.message.chat_id, text=hello)

        self.deployer.deploy()

    def unknown(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

    def run(self):
        self.updater.start_polling()

if __name__ == '__main__':
    cli()
