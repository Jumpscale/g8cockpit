# Telegram Bot for AYS

## Description

This bot let you manage and run some `ays` projects (repositories) via Telegram.

## Basic demo

This is a basic way to see how the bot works:
```
/start
/repo select
/blueprint create
/blueprint execute
/run create 
/run exec
```

## Complete usage

The first step to make this bot working for you is to talk with the bot and send `/start` command. Internally this create an environment for you.

Now you are able to create/delete some projects (repositories) via `/repo` command:
 * `/repo list `:  will list your projects and tell you which is your running project
 * `/repo select [name]`: will create or checkout (change current) project called `[name]`
 * `/repo delete [name]`: will delete the `[name]` project

A project is a ays repository, to customize it, you'll need to upload some blueprints. Simply upload files to add them to blueprints directory.

You can manage blueprints like projects:
 * `/blueprint list`: will list your project's blueprints
 * `/blueprint delete [name]`: will delete `[name]` blueprint
 * `/blueprint show [name]`: will show you the blueprint `[name]` contents

To add blueprint, you only can upload files.

When you have a project with blueprints, you can apply some `ays` stuff on it:
 * `/run create`
 * `/run exec`
 * ...


## Installation
Generate a token via @botfather on Telegram, then use it to launch this bot:

within your code directory `[depends on your configuration]/github/jumpscale/jscockpit/ays_bot`:

To run the bot use in terminal :  
`jspython ays-bot`
This will look for the configuration in the path you run the bot from,  
to adjust that use the `--config` or `-c` option and specify a different path.

```
Options:
  -c, --config TEXT  path to the config file
  -token TEXT        override token specified in config
```
