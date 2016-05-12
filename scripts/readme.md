# Scripts

This directory contains 2 scripts:
- buiding.py:
It generates the cockpit docker image from scratch
- telegram-bot:
Start a small telegram bot that allow client to deploy a cockpit over telegram.

## requirements

```
pip3 install python-telegram-bot
```


## Usage
### building.py
```
Usage: building.py [OPTIONS] COMMAND [ARGS]...

Options:
  --debug  enable debug mode
  --help   Show this message and exit.

Commands:
  build    Build g8cockpit docker image
  update   Update the git repo used during installation...
  upgrade  upgrade the jumpscale/g8cockpit docker image.
```

## telegram-bot

```
./telegram-bot --help
Usage: telegram-bot [OPTIONS]

Options:
  -c, --config TEXT  path to the config file
  --help             Show this message and exit.
```  

Config file example for the telegram bot:


```toml
[bot]
# bot token from @botfather
token = "CHANGEME"

# address of the G8 you want to propose to the users
# during deployment.
[g8.be-conv-2]
adress = "be-conv-2.demo.greenitglobe.com"
[g8.be-conv-3]
adress = "be-conv-3.demo.greenitglobe.com"

# credentials for the dns cluster.
# if you don't specify the credentials, they will be ask to the user during deployment
[dns]
login = "admin"
password = "CHANGEME"
```
