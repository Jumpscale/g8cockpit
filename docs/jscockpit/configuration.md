# Configuration


The cockpit use [itsyou.online](https://itsyou.online/) to authenticate the users. A cockpit is always deployed for a specific organization on [itsyou.online](https://itsyou.online/). In order to make sure only member of this organization can interact with the cockpit we use oauth2.  
- For the REST API we use [JWT](https://jwt.io/) tokens to authenticate the requests
- For the telegram bot we ask the user to authenticate on [itsyou.online](https://itsyou.online/) direclty the first time he interact with the bot.

## Configuration file for JSCockpit
This configuration file is generated automaticly during the deployment of the cockpit. But for development if you need to just star the jscockpit server, create a config file manually.
Here is an example:
```toml
[oauth]
client_secret = 'okla3Z2PLNmxu9sdfgrtFaOyBlCmOz4OeNW-V1lJh66OBtuqkk7_5H'
client_id = 'MyID'
redirect_uri = 'https://mycockpit.aydo.com/oauth/callback'
organization = 'MyID'
jwt_key = "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n2\n7MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny6\n6+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv\n-----END PUBLIC KEY-----"
itsyouonlinehost = 'https://itsyou.online'

[api.ays]
active = true
host = "0.0.0.0"
port = 5000

[bot]
token = "205766488:AAEizYAolZddhL-G21oOM5JL1lmOf9slh4s"

[mail]
host = "0.0.0.0"
port = 25
```

**Generate telegram bot token.**
- connect to telegram and talk to @botfather.
- execute the command `/newbot` and choose a name and username for your bot
- @botfather should give you a token, add it to the main.py file


**Add command description to your bot.**
- type `/setcommands` in @botfather, choose your bot and past these lines :

```
start - Start discussion with the bot
repo - Manage your AYS repositories
blueprint - Manage your blueprints project
service - Perform actions on your service instances
help - Show you what I can do
```

## Start cockpit
```bash
jspython cockpit start --config config.toml
```
### Cockpit CLI command:
```
./cockpit --help
Usage: cockpit [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  clean_cache  Empty Oauth cache for telegram bot
  start        Start cockpit server

```
- **start** : start cockpit server
- **clean_cache** : Empty cache that store oauth authentification for telegram bot