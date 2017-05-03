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
g8client__{environment}:
  url: '{url}'
  jwt: '{jwt}'
  account: '{account}'

account__{account-name}:
  description: '{description}'
  g8client: '{environment}'
  location: '{location}'
  accountusers:
  - '{admin}'
  maxMemoryCapacity: {maxMemoryCapacity}
  maxCPUCapacity: {maxCPUCapacity}
  maxNumPublicIP: {maxNumPublicIP}
  maxDiskCapacity: {maxDiskCapacity}

actions:
  - action: install    
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
- `{description}`: description for the account
- `{maxMemoryCapacity}`: total memory capacity in MB available in the account
- `{maxCPUCapacity}`: number of virtual CPU core available in the account
- `{maxNumPublicIP}`: number of external IP addresses available in the account
- `{maxDiskCapacity}`: total disk capacity in GB available in the account
