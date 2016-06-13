# installation
There is two way of deploying a new cockpit.
- Using our cockpit deployer bot on Telegram
- Using AtYourService

## Using Cockpit deployer bot:
Talk to `@g8cockpitbot` on telegram.  
The bot will ask you some questions about the cockpit you want to deploy. After answering the questions, the bot will take care of deploying a new cockpit on one G8.  
At the end of the deployement the bot will send you the information to access your newly created cockpit.

Detail about the questions:
- **Organization**: A cockpit is always deployed for an Organization. The Organization need to exists on https://itsyou.online/.
- **Url of the G8**: The bot will propose you multiple G8 where to deploy your cockpit. choose one of the G8. Notice you need to have an account on the choosen G8.
- **Login**: Your account on the selected G8
- **Password**: the password of your account on the selected G8
- **Telegram token**: The cockpit runs a telegram bot thus you need to create a bot on telegram and past the token of the bot.
- **VDC Name**: The name of the vdc on the selected G8 where you want to deploy your cockpit. If the VDC doesn't exists, it will be created
- **Domain**: Choose the domain name you want for your cockpit. This can be anything as long as it's a valid domain name.

## Using AtYourService:
If you have a system with JumpScale installed, you can use AtYourService to create a new cockpit.

- create a AYS repository:
```bash
mkdir /opt/code/ays_cockpit
mkdir /opt/code/ays_cockpit/blueprints
touch /opt/code/ays_cockpit/.ays
```
- Replace the value in this blueprint:

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
- Copy it to the blueprints folder  
```bash
cp bp.yml /opt/code/ays_cockpit/blueprints
```
- Init and install the blueprint:
```bash
cd /opt/code/ays_cockpit
ays init
ays install
```