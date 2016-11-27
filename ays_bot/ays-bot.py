#!/usr/local/bin/jspython

import click
from JumpScale import j
from telegrambot.Bot import TGBot
from telegrambot.Oauth import app
from multiprocessing import Process


@click.command()
@click.option('--config', '-c', help='path to the config file', default='config.toml')
@click.option('-token', help='override token specified in config', default=None)
def cli(config, token):
    cfg = j.data.serializer.toml.load(config)
    if token:
        cfg['access_token'] = token

    # start flask server for aouth workflow
    app.config.update(cfg['oauth'])
    p = Process(target=app.run, kwargs={
        'host': cfg['oauth'].get('host', '127.0.0.1'),
        'port': cfg['oauth'].get('port', 5000)
    })
    p.start()

    # start bot
    bot = TGBot(cfg)
    bot.start()

    bot.join()
    p.join()


if __name__ == '__main__':
    cli()
