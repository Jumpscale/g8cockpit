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

## How to Start
create a configuration file. Format used for config file is toml. Here is an example:
```toml
[bot]
# token from telegram
token='205766488:AAFBNvCFzNUaKBwND7oHkriEkmFvnVsfLMeg'

[mail]
# listen port of the SMTP server
port=25

[api]
# listen address and port of the REST API
host="0.0.0.0"
port=5000
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

**Start cockpit**
```bash
jspython cockpit --config config.toml
```
