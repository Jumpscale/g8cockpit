# Gevent based cockpit

## Architecture
The cockpit is composed of multiple servers.  
The main module (main.py) has the only role of loading configuration and starting all the component.  
Components communicate using publish/subscribe mechanism.  
Event object can be found at https://github.com/Jumpscale/jumpscale_core8/blob/ays8fix/lib/JumpScale/data/models/CockpitEventModels.py

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
Proper configuration is not implemented yet. Change the config in the main.py file itself for now. Then start all the servers.
```
jspython main.py
```
