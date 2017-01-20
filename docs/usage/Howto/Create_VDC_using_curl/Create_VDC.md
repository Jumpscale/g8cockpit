## How to create a VDC

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
