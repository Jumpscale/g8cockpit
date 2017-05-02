## How to create an account

For creating an account use the **account** actor template, available here: https://github.com/Jumpscale/ays_jumpscale8/tree/master/templates/ovc/account


**Minimal blueprint**:

```
g8client__{environment}:
  url: '{url}'
  jwt: '{jwt}'
  account: '{account}'

account__{account-name}:
  g8client: '{environment}'
  location: '{location}'
  accountusers:
  - '{admin}'

actions:
  - action: install    
```

**Full blueprint**:

```
description = type:multiline

g8client = type:str consume:'g8client' auto
accountusers = list type:str consume:'uservdc' auto

accountID = type:int default:0

maxMemoryCapacity = type:int default:-1
maxCPUCapacity = type:int default:-1
maxNumPublicIP = type:int default:-1
maxDiskCapacity = type:int default:-1

```

Values:

- `{environment}`: environment name for referencing elsewhere in the same blueprint or other blueprint in the repository
- `{url}`: URL to to the G8 environment, e.g. `gig.demo.greenitglobe.com`
- `{login}`: username on the targeted G8 environment
- `{password}`: password for the username
- `{jwt}`: JWT
- `{account}`: account on the targeted G8 environment used for the S3 server
- `{location}`: location
- `{account-name}`: new account
- `{admin}`: username of first admin
