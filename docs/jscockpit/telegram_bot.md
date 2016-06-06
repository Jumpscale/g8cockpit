# Telegram bot
The telegram bot of your cockpit allow you to execute AYS blueprints and explore the AYS repository present on your cockpit.

## Commands
- /Start:  
This is the first command you will execute when talking to the bot for the first time.
The bot will redirect you to https://itsyou.online to make sure you're part of the organization of the cockpit.
- /Repo:
 - select: Select a repository to work on.
 - list: list all repositories.
 - create: create a new repository.
 - delete: remove a repositories.
- /Blueprint:
 - add: create a new blueprint and execute it.
 - list: list all blueprints and display the content.
 - delete: uninstall service from the blueprint then delete it.
- /Service
 - list: List all services from the selected repository.
 - inspect: Disaplay information about a service.
 - execute: execute an action on one or a group of services.
- /Help: Display help
