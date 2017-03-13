## How to create a VDC

For creating a virtual datacenter (VDC) use the **vdc** actor template, available here: https://github.com/Jumpscale/ays_jumpscale8/tree/master/templates/ovc/vdc


**Minimal blueprint**:

```
g8client__{environment}:
  url: '{url}'
  login: '{login}'
  password: '{password}'
  account: '{account}'

vdc__{vdc-name}:
  g8client: '{environment}'
  location: '{location}'

actions:
  - action: install    
```

**Full blueprint**:

```
g8client__{environment}:
  url: '{url}'
  login: '{login}'
  password: '{password}'
  account: '{account}'

uservdc__{username1}:
  g8client: '{environment}'
  email: '{email1}'
  provider: 'itsyouonline'

uservdc__{username2}:
  g8client: '{environment}'
  email: '{email2}'
  provider: 'itsyouonline'

vdcfarm__{vdcfarm}:

vdc__{vdc-name}:
  description: '{description}'
  vdcfarm: '{vdcfarm}'
  g8client: '{environment}'
  account: '{account}'
  location: '{location}'
  externalNetworkID: `{externalNetworkID}`

  uservdc:
    - `{username1}`
    - `{username2}`

  maxMemoryCapacity: {maxMemoryCapacity}
  maxCPUCapacity: {maxCPUCapacity}
  maxDiskCapacity: {maxDiskCapacity}
  maxNumPublicIP: {maxNumPublicIP}

actions:
  - action: install    
```

Values:

- `{environment}`: environment name for referencing elsewhere in the same blueprint or other blueprint in the repository
- `{url}`: URL to to the G8 environment, e.g. `gig.demo.greenitglobe.com`
- `{login}`: username on the targeted G8 environment
- `{password}`: password for the username
- `{account}`: account on the targeted G8 environment used for the S3 server
- `{username1}` and `{username2}`: ItsYou.online usernames of the users that will get Admin access to the the VDC
- `{email1}` and `{email1}`: email addresses of the users that will get Admin access
- `{vdc-name}`: name of the VDC that will be created for the S3 server, and if a VDC with the specified name already exists then that VDC will be used
- `{description}`:  optional description for the VDC
- `{vdcfarm}`: optional name of the VDC Farm to logically group the VDC into a VDC farm; if not specified a new VDC farm will be created
- `{location}`: location where the VDC needs to be created
- `{externalNetworkID}`: ID of the external network to which the VDC needs to get connected; of not specified then it will default to the first/default external network
- `{maxMemoryCapacity}`: available memory in GB for all virtual machines in the VDC
- `{maxCPUCapacity}`: total number of available virtual CPU core that can be used by the virtual machines in the VDC
- `{maxDiskCapacity}`: available disk capacity in GiB for all virtual disks in the VDC
- `{maxNumPublicIP}`: number of external IP addresses that can be used by the VDC


Future attribute:
- `allowedVMSizes`: listing all IDs of the VM sizes that are allowed in this cloud space


Also possible:
In stead of providing a login and password for the g8client actor, you can also provide a JWT string: `jwt= type:str default:''``
See: https://github.com/Jumpscale/ays_jumpscale8/blob/8.1.1/templates/clients/g8client/schema.hrd


Return values:
cloudspaceID = type:int default:0
...



Here's an example blueprint for creating a VDC:

```
g8client__cl:
  url: 'uk-g8-1.demo.greenitglobe.com'
  login: '***'
  password: '***'
  account: '***'

vdc__myvdc:
  g8client: 'cl'
  account: '***'
  location: 'uk-g8-1'

actions:
  - action: install
```


Also:

```
cd /optvar/cockpit_repos
ays create-repo
ays blueprint
ays run
ays discover
ays restore
ays state
```

Below we discuss creating a VDC step by step using curl commands:

- [Get an OAuth token with Client Credentials Flow](#get-token)
- [Get a JWT to talk to the Cockpit](#get-JWT)
- [Create a new repository](#create-repository)
- [Create blueprint for a g8client service instance](#g8client-blueprint)
- [Execute the g8client blueprint](#g8client-execute)
- [Create blueprint for a user](#user-blueprint)
- [Execute the user blueprint](#user-execute)
- [Create blueprint for new VDC](#vdc-blueprint)
- [Execute the VDC blueprint](#vdc-execute)
- [Start a run to actually deploy the VDC](#install-VDC)


<a id="get-token"></a>
### Get an OAuth token with Client Credentials Flow

```
curl -d "grant_type=client_credentials&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}" /
     https://itsyou.online/v1/oauth/access_token
```

<a id="get-JWT"></a>
### Get a JWT to talk to the Cockpit

```
curl -H "Authorization: token OAUTH-TOKEN" /
     https://itsyou.online/v1/oauth/jwt?aud=client_id
```

<a id="create-repository"></a>
### Create a new repository

```
curl -H "Authorization: bearer JWT"  /
     -H "Content-Type: application/json" /
     -d '{"name":"test-repo"}' /
     https://{address}:5000/ays/repository
```

<a id="g8client-blueprint"></a>
### Create blueprint for a g8client service instance

```
curl -H "Authorization: bearer JWT"  /
     -H "Content-Type: application/json" /
     -d '{"name":"cl.yaml","content":"g8client__cl:\n  g8.url: uk-g8-1.demo.greenitglobe.com\n  g8.login: ***\n  g8.password: ***\n  g8.account:***"}'
     https://{address}:5000/ays/repository/
```

<a id="g8client-execute"></a>
### Execute the g8client blueprint

```
curl -H "Authorization: bearer JWT"  /  
     https://{address}:5000/ays/repository/{repository-name}/blueprint/cl.yaml
```

<a id="user-blueprint"></a>
### Create blueprint for a user

```
curl -H "Authorization: bearer JWT"  /
     -H "Content-Type: application/json" /
     -d '{"name":"user1.yaml","content":"ovc_user__user1:\n  g8.client.name: 'cl'\n  username: 'mike'\n  email: 'mike@gmail.com'\n  provider: 'itsyouonline'"}'
     https://{address}:5000/ays/repository/
```

<a id="user-execute"></a>
### Execute the user blueprint

```
curl -H "Authorization: bearer JWT"  /  
     https://{address}:5000/ays/repository/{repository-name}/blueprint/user1.yaml
```

<a id="vdc-blueprint"></a>
### Create blueprint for new VDC

```
curl -H "Authorization: bearer JWT"  /
     -H "Content-Type: application/json" /
     -d '{"name":"myvdc.yaml","content":"vdc__myvdc:\n  g8client: 'cl'\n  location: uk-g8-1"}'
     https://{address}:5000/ays/repository/
```

<a id="vdc-execute"></a>
### Execute the VDC blueprint

```
curl -H "Authorization: bearer JWT"  /  
     https:/{address}:5000/ays/repository/{repository-name}/blueprint/myvdc.yaml
```

<a id="install-VDC"></a>
### Start a run to actually deploy the VDC

```
curl -X POST
     -H "Authorization: bearer JWT" /
     http://{address}:5000/ays/repository/{repository-name}/aysrun | python -m json.tool
```
