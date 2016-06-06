# Architecture
The cockpit is composed of multiple servers.  
The components communicate using publish/subscribe mechanism.  

{% plantuml %}
@startuml
title Cockpit
[REST Server] as rest
[Mail Server] as mail
[Core] as core
[Telegram bot] as telegram
database "Redis" {
  node Topics{
  }
}


rest .up. HTTP : use
mail .down. SMTP : use
telegram .down. TelegramBotAPI : use

rest -down-> Topics : publish
mail .left.> Topics : publish
core <-right-> Topics : pub/sub
telegram <-up-> Topics: pub/sub


@enduml
{% endplantuml %}

## Components :
### Main module
The main module has the only role of loading configuration and starting all the component.
Any class with a start and stop method can be added as a server. The start method should not be blocking

### Core
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

