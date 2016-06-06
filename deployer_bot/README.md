# Cockpit deployer bot

This telegram bot is used to allow people to easily deploy a [JSCockpit](https://github.com/Jumpscale/jscockpit/tree/master/app).

This bot is composed of two components, the bot itself and a small flask app that is used to receive callback from itsyou.online for oauth workflow. Both need to be started for the bot to properly work.  

## How to start the bot
To start the bot you can use the little CLI provided, [telegram-bot](telegram-bot).

```bash
Usage: telegram-bot [OPTIONS]

Options:
  -c, --config TEXT  path to the config file
  --help             Show this message and exit.

```  

You need create a configuration file. By default the bot look for a `config.toml` file in the current directory, but you can specify a path using the `--config` argument. Here a example of the required configuration

```toml
[bot]
# bot token from @botfather
token = "205766488:AAEizHUvxZddhL-G21oOM5JL1lmOf9slh4s"

# address of the G8 you want to propose to the users
# during deployment.
[g8.be-scale-1]
address = "be-scale-1.demo.greenitglobe.com"

# credentials for the dns cluster.
# if you don't specify the credentials, they will be ask to the user during deployment
[dns]
login = "login"
password = "password"
sshkey = "path of private key"

[oauth]
host = '0.0.0.0'
port = 5000
# adress of you oauth server where itsyouonline should send callback. Make sure the same URL is used in itsyou.online.
redirect_uri = "https://deployerbot.com/callback"
# CLient ID from your app on itsyou.online
client_id = 'myId'
# CLient secret from your on in itsyou.online
client_secret = 'IuDUBE--6NMQS1OH-UmcOijhT7Uq2lPdWnJ74hMSMqgKjjQhtZDC'
itsyouonlinehost = "https://itsyou.online"
jwt_key = '''
itsyou.online public key for jwt signing : see https://github.com/itsyouonline/identityserver/blob/master/docs/oauth2/jwt.md
'''
```

Make sure the `May be used in client credentials gran type` is enable when creating the client secret for this bot

### DNS config:
To have detail about how to configure the DNS part, check https://gig.gitbooks.io/ovcdoc_internal/content/InternalIT/internal_it.html
