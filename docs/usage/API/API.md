## REST API

The Cockpit exposes its functionality through a REST API.

The REST interface is generated from a [RAML](http://raml.org/) specification using [go-raml](https://github.com/jumpscale/go-raml). The RAML file is located at https://github.com/Jumpscale/jscockpit/blob/master/jscockpit/ays_api/specifications/api.raml

The REST API is documented in the **API Console** of your portal. See the section about the [API Console](../API_console/API_Console.md) for more information.


### API Client

Go-raml also supports generation of the client for an API. A raw version of a Python client can be found at https://github.com/Jumpscale/jscockpit/tree/master/client.  
[JumpScale](https://github.com/Jumpscale/jumpscale_core8) makes it even more user-friendly.


### How to use the Python client

The REST API of the Cockpit uses [JWT](https://jwt.io/) to authenticate requests. 

See the section about [how to generate JWT tokens](../JWT/JWT.md).

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
