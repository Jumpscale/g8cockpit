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
CLIENT_ID="..."
CLIENT_SECRET="..."
curl -d "grant_type=client_credentials&client_id=${CLIENT_ID}&client_secret=${CLIENT_SECRET}" \
     https://itsyou.online/v1/oauth/access_token > token.txt
ACCESS_TOKEN=$(awk '{split($0,a,",");split(a[1],b,":");gsub(/\"/,"",b[2]);print b[2]}' token.txt)
echo $ACCESS_TOKEN
```

<a id="get-JWT"></a>
### Get a JWT to talk to the Cockpit

```
JWT=$(curl -H "Authorization: token ${ACCESS_TOKEN}" https://itsyou.online/v1/oauth/jwt?aud=${CLIENT_ID})
echo $JWT
```

<a id="create-repository"></a>
### Create a new repository

```
REPO_NAME="..."
GIT_URL="https://github.com/user/reponame"
BASE_URL="<IP-address>"
AYS_PORT="5000"
curl -H "Authorization: bearer $JWT" \
     -H "Content-Type: application/json" \
     -d '{"name":"'$REPO_NAME'", "git_url":"'$GIT_URL'"}' \
     https://$BASE_URL:$AYS_PORT/ays/repository
```

<a id="g8client-blueprint"></a>
### Create blueprint for a g8client service instance

```
G8_URL="..."
LOGIN="..."
PASSWORD="..."
ACCOUNT="..."
curl -H "Authorization: bearer $JWT" \
     -H "Content-Type: application/json" \
     -d '{"name":"cl.yaml", "content":"g8client__cl:\n  url: '$G8_URL'\n  login: '$LOGIN'\n  password: '$PASSWORD'\n  account: '$ACCOUNT'"}' \
     https://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint
```


<a id="g8client-execute"></a>
### Execute the g8client blueprint

```
curl -H "Authorization: bearer $JWT" \
     https://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint/cl.yaml
```

<a id="user-blueprint"></a>
### Create blueprint for a user

```
USERNAME2="..."
EMAIL="..."
curl -H "Authorization: bearer $JWT" \
     -H "Content-Type: application/json" \
     -d '{"name":"user1.yaml","content":"ovc_user__user1:\n  g8.client.name: cl\n  username: '$USERNAME2'\n  email: '$EMAIL'\n  provider: itsyouonline"}' \
     https://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint
```

<a id="user-execute"></a>
### Execute the user blueprint

```
curl -H "Authorization: bearer $JWT" \  
     https://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint/user1.yaml
```

<a id="vdc-blueprint"></a>
### Create blueprint for new VDC

In order to create a VDC you need the name of the G8 location and the ID of the external network.

In order to get a list of available external networks for a given account use the Cloud API, here for account with ID=23:

```
curl -X POST \
     --header 'Content-Type: application/x-www-form-urlencoded' \
     --header 'Accept: application/json'
     -d 'accountId=23' \
     https://$BASE_URL/restmachine/cloudapi/externalnetwork/list'
```

In order to get this list of available locations use the following Cloud API:
```
curl -X POST \
     --header 'Content-Type: application/json' \
     --header 'Accept: application/json' \
     https://be-gen-1.demo.greenitglobe.com/restmachine/cloudapi/locations/list
```

```
LOCATION="..."
EXTERNAL_NETWORK="..."

curl -H "Authorization: bearer $JWT" \
     -H "Content-Type: application/json" \
     -d '{"name":"myvdc.yaml","content":"vdc__myvdc:\n  g8client: cl\n  location: '$LOCATION'\n  externalNetworkID: '$EXTERNAL_NETWORK'"}' \
     https://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint
```

<a id="vdc-execute"></a>
### Execute the VDC blueprint

```
curl -H "Authorization: bearer $JWT" \
     https://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint/myvdc.yaml
```

<a id="vdc-execute"></a>
### Create a blueprint for calling the install actions

```
curl -H "Authorization: bearer $JWT" \
     -H "Content-Type: application/json" \
     -d '{"name":"actions.yaml","content":"actions:\n  - action: install\n"}' \
     https://$BASE_URL:$AYS_PORT/ays/repository/$REPO_NAME/blueprint
```


<a id="vdc-execute"></a>
### Execute the install actions blueprint

...


<a id="install-VDC"></a>
### Start a run to actually deploy the VDC

```
curl -X POST
     -H "Authorization: bearer $JWT" \
     http://{address}:5000/ays/repository/{repository-name}/aysrun | python -m json.tool
```
