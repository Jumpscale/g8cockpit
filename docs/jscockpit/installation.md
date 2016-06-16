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