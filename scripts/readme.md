# Scripts

This directory contains three Scripts:
- buiding.py:
It generates the cockpit docker image from scratch
- cockpit.py:
Used to manually deploy a cockpit.
- telegram-bot:
Start a small telegram bot that allow client to deploy a cockpit over telegram.


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
### cockpit.py
```
Usage: cockpit.py install [OPTIONS]

  Start installation process of a new G8Cockpit

Options:
  --repo-url TEXT         Url of the git repository where to store the ays
                          repo.
  --ovc-url TEXT          Url of the Gener8 where to deploy cockpit
  --ovc-login TEXT        Login of your account on Gener8 where to deploy
                          cockpit
  --ovc-password TEXT     Password of your account on the Gener8 where to
                          deploy cockpit
  --ovc-account TEXT      Account to use on the Gener8 where to deploy cockpit
  --ovc-vdc TEXT          Name of the Virtual Data center where to deploy the
                          G8Cockpit
  --ovc-location TEXT     Location of the vdc
  --dns-login TEXT        Password of your account on the dns cluster
  --dns-password TEXT     Password of your account on the dns cluster
  --domain TEXT           Dns to give to the cockpit. Name will be append with
                          .cockpit.aydo.com
  --sshkey TEXT           Name of the ssh key to authorize on the G8Cockpit.
                          key are fetch from ssh-agent.
  --portal-password TEXT  Admin password of the portal
  --expose-ssh            Expose ssh of the G8Cockpit over HTTP
  --bot-token TEXT        Telegram token of your bot
  --gid TEXT              Grid ID to give to the controller
  --dev                   Use staging environment for caddy. Enable this
                          during testing to avoid running up adgains
                          letsencrypt rate limits
  --help                  Show this message and exit.
```

You can start the script with all the options filled in like  
```
./cockpit2.py  --debug install  --ovc-url be-conv-2.demo.greenitglobe.com --ovc-login ovclogin --ovc-password secret --ovc-vdc cockpit --dns-login login --dns-password secret --domain mycockpit --repo-url https://github.com/user/repo --sshkey id_rsa --portal-password secret --gid 1 --bot-token telegramtoken```

Or you can just run the script without any options and it will interactively ask you the information as the installation is going.
`./cockpit.py install`


remarks for mothership1 usage
- mothership 1 gener8 url = www.mothership1.com
- virtual datacenter needs to exist, can be the default one
- locations are: ca1,uk1,eu1 (to know location of your space got to space settings [https://www.mothership1.com/wiki_gcb/CloudSpaceSettings#/list] it will print e.g. canada


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
