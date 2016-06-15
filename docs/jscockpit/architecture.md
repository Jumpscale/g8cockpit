# Architecture

The cockpit is composed of multiple components/servers, which are implemented in Python modules.

These servers communicate using publish/subscribe mechanism via Redis.

{% plantuml %}
@startuml
title Cockpit
[REST Server] as rest
[Mail Server] as mail
[Core] as core
[Telegram Chatbot] as telegram
database "Redis" {
  node Topics{
  }
}

rest .up. HTTP : use
mail .down. SMTP : use
telegram .down. TelegramChatbotAPI : use

rest -down-> Topics : publish
mail -left-> Topics : publish
core <-right-> Topics : pub/sub
telegram <-up-> Topics: pub/sub


@enduml
{% endplantuml %}

## Components

### Main module (not shown in the above picure)

The main module is the Python module that starts the Cockpit.

The only role of the main module is loading configuration and starting all the other components.

Any class with a start and stop method can be started from there as a server. The start method should not be blocking.


### Core

This Core module holds the logic of the AYS chatbot.
  
It subscribes to all events and implements some handlers based on the type of event it receives.
  
The core module is responsible for executing the actions of services when an execute event is received.


### Mail

The Mail module implements a Simple SMTP server.

It saves the attachments of mails locally and generates an event for every mail it received.


### Telegram Chatbot

Holds the logic for all communication over Telegram.  

Some of the chatbot commands generate:

- project create/delete
- action execute


### REST Server

Any Web Server Gateway Interface (WSGI) compliant server can be added. 

In the initial implementation we only have one REST Server, exposing the AYS REST APIs. 

Most of the time it's the REST Server that generates events based on the requests it receives.