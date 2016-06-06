# Gevent based cockpit

## Architecture
The cockpit is composed of multiple servers.  
Components communicate using publish/subscribe mechanism.  
Event object can be found at https://github.com/Jumpscale/jumpscale_core8/blob/ays8fix/lib/JumpScale/data/models/CockpitEventModels.py

## main module
The main module has the only role of loading configuration and starting all the component.
Any class with a start and stop method can be added as a server. The start method should not be blocking

### ays_bot
This module holds the logic of the AYS bot.  
It subscribe to all events and implement some handler base on the type of event received.  
Responsible to execute the actions of services when execute event is receive.

### Mail
Simple SMTP server.  
Save the attachments of mail locally and generate an event for every mail. received, save

### Telegram bot
Logic for communication over Telegram.  
Commands that generate generate events.
- project create/delete
- action execute

### APIs
Any number of WSGI server can be added. Most of the time it's REST server that generates event based on the request they receive.

## Oauth2
The cockpit use itsyou.online to authenticate the users. A cockpit is always deployed for a specific organization on itsyou.online. In order to make sure only member of this organization can interact with the cockpit we use oauth2.  
- For the REST API we use [JWT](https://jwt.io/) tokens to authenticate the requests
- For the telegram bot we ask the user to authenticate on itsyou.online direclty the first time he interact with the bot.

## How to Start
create a configuration file. Format used for config file is toml. Here is an example:
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