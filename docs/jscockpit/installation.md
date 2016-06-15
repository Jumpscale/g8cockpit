# Installation

There are two ways of deploying a new Cockpit:

- Using our Cockpit Deployer Chatbot on Telegram
- Using AtYourService


## Using Cockpit Deployer Chatbot

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


## Using AtYourService

If you have a system with JumpScale installed, you can also use AtYourService to create a new Cockpit.

- Create a AYS service repository:

```bash
mkdir /opt/code/ays_cockpit
mkdir /opt/code/ays_cockpit/blueprints
touch /opt/code/ays_cockpit/.ays
```

- Replace the values in this blueprint:

```yaml
g8client__main:
  g8.url: '{g8_url}'
  g8.login: '{g8_login}'
  g8.password: '{g8_password}'
  g8.account: '{g8_account}'

cockpit__pilot:
  telegram.token: '{telegram_token}'
  cockpit.name: '{cockpit_name}'
  dns.sshkey: '{dns_sshkey}'
  dns.domain: '{dns_domain}'
  oauth.client_secret: '{oauth_secret}'
  oauth.client_id: '{oauth_id}'
  oauth.organization: '{oauth_organization}'
  oauth.jwt_key: '{oauth_jwtkey}'
```

- Copy the blueprint into the blueprints subdirectory:  

```bash
cp bp.yml /opt/code/ays_cockpit/blueprints
```

- Init and install the blueprint:

```bash
cd /opt/code/ays_cockpit
ays init
ays install
```