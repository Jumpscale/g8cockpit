# REST API

The Cockpit exposes its functionality with a REST API.
 
The REST interface is generated from a [RAML](http://raml.org/) specification using [go-raml](https://github.com/jumpscale/go-raml).

RAML file is located at https://github.com/Jumpscale/jscockpit/blob/master/jscockpit/ays_api/specifications/api.raml

A live documentation about the REST API can is available in your Cockpit at the address :
https://my-cockpit.com/api/apidocs/index.html


## API Client

Go-raml also supports generation of the client for an API. A raw version of the client can be found at https://github.com/Jumpscale/jscockpit/tree/master/client.  
[JumpScale](https://github.com/Jumpscale/jumpscale_core8) makes it even more user-friendly.

### How to use

The REST API of the Cockpit uses [JWT](https://jwt.io/) to authenticate requests.

The Cockpit Portal provides an easy way to generate such a JWT token:

- Go to the `/cockpit/jwt` page on the Cockpit Portal
- Use the dropdown button and click on **Generate JWT token**

![generate jwt token](2016-06-10_321x155_scrot.png)

Once you have your JWT token, usage of the client is trivial:

```python
jwt = '...JWT from cockpit portal...'
base_url = 'https://my-cockpit.com/api'
client = j.clients.cockpit.getClient(base_url, jwt)
```

List of available methods in the client:
```
client.createNewBlueprint              client.deleteRepository                client.executeServiceActionByRole      client.getTemplate                     client.listServices
client.createNewRepository             client.deleteServiceByInstance         client.getBlueprint                    client.listBlueprints                  client.listServicesByRole
client.createNewTemplate               client.executeBlueprint                client.getRepository                   client.listRepositories                client.listTemplates
client.deleteBlueprint                 client.executeServiceActionByInstance  client.getServiceByInstance            client.listServiceActions              client.updateBlueprint
```