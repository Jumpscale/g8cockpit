# REST API
The JSCockpit exposes its functionality with a REST API.  
The REST interface is generated from a [raml](http://raml.org/) specification using [go-raml](https://github.com/jumpscale/go-raml).
Raml file is located at https://github.com/Jumpscale/jscockpit/blob/master/jscockpit/ays_api/specifications/api.raml

A live documentation about the REST API can is available in your cockpit at the address :
https://my-cockpit.com/api/apidocs/index.html

## API Client
Go-raml also support generation of the client of an API. A raw version of the client can be found at https://github.com/Jumpscale/jscockpit/tree/master/client.  
But to make the usage of this client even more user-friendly, an improved version is available in [JumpScale](https://github.com/Jumpscale/jumpscale_core8).

### How to use
The REST API of the cockpit uses [JWT](https://jwt.io/) to authenticate requests. The cockpit portal provide an easy way to generate such a token.

TODO insert screeshot of the JWT page.

Once you have your JWT token, usage of the client is trivial:
```python
jwt = '...JWT from cockpit portal...'
base_url = 'https://my-cockpit.com/api'
client = j.clients.cockpit.getClient(base_url, jwt)
```

List of available method in the client:
```
client.createNewBlueprint              client.deleteRepository                client.executeServiceActionByRole      client.getTemplate                     client.listServices
client.createNewRepository             client.deleteServiceByInstance         client.getBlueprint                    client.listBlueprints                  client.listServicesByRole
client.createNewTemplate               client.executeBlueprint                client.getRepository                   client.listRepositories                client.listTemplates
client.deleteBlueprint                 client.executeServiceActionByInstance  client.getServiceByInstance            client.listServiceActions              client.updateBlueprint
```