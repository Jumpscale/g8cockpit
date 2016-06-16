# Installation

There are two ways of install a new Cockpit:

- Using the **Cockpit Deployer Chatbot** on Telegram
- Using AtYourService


## Using Cockpit Deployer Chatbot

An instance of the **Cockpit Deployer Chatbot** is active as `@g8cockpitbot` on Telegram.  

You can also install your own instance by following the [Cockpit Deployer Chartbot installation instructions](../deployer_bot/installation.md).

Follow the [Cockpit Deployer Chartbot usage instructions](../deployer_bot/usage.md) in order to install your Cockpit.


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

Description of the values:
- g8.url : URL of the G8 where you want to deploy the cockpit. e.g: `be-scale-1.demo.greenitglobe.com`
- g8.login: Login of your account on the g8
- g8.password: Password of your account on the g8
- g8.account: Account name if different from login.
- telegram.token: Token from telegram. Given by @botfather when you create a new bot.
- cockpit.name: Can be anything
dns.sshkey: Path to the sshkey of the DNS server. see https://gig.gitbooks.io/ovcdoc_internal/content/InternalIT/internal_it.html for detail about DNS infrastructure
- dns.domain: sub domain you want for your cockpit. e.g: if you choose `mycockpit`, the domain will be `mycockpit.barcelona.aydo.com`
- oauth.client_secret: Client secret for of your Organization from your on in itsyou.online
- oauth.client_id: Client Id for of your Organization from your on in itsyou.online
- oauth.organization: Name of the organization of this cockpit
- oauth.jwt_key: itsyou.online public key for jwt signing. See https://github.com/itsyouonline/identityserver/blob/master/docs/oauth2/jwt.md

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