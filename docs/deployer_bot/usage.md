# Using the Cockpit Deployer Chatbot

An instance of the **Cockpit Deployer Chatbot** is active as `@g8cockpitbot` on Telegram.  

You can also install your own instance by following the [Cockpit Deployer Chartbot installation instructions](../deployer_bot/installation.md).

Talk to `@g8cockpitbot` on Telegram.  

The chatbot will ask you some questions about the Cockpit you want to deploy. After answering the questions, the chatbot will take care of deploying a new Cockpit on a G8.  
At the end of the deployement the chatbot will send you the information to access/use your newly created Cockpit.

Detail about the questions:

- **Organization**: a cockpit is always deployed for an organization, which needs to exists on https://itsyou.online/
- **URL of the G8**: the chatbot will propose you multiple G8s where you can deploy your Cockpit, make sure to choose one where you have a username with access to a (cloud) account
- **Login**: Your username on the selected G8
- **Password**: the password of your username on the selected G8
- **Telegram token**: next to a web portal the Cockpit also comes a Telegram chatbot interface, that you will need the create by talking to @botfather, another chatbot, from which you will receive an API token to paste into the conversation with @g8cockpitbot
- **VDC Name**: the name of the VDC on the selected G8 where you want to deploy your Cockpit, if the VDC doesn't exist yes, it will be created
- **Domain**: the domain name you want for your Cockpit, this can be anything as long as it's a valid/unique domain name