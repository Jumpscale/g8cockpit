## How to list all Repositories

- [In the Cockpit Portal](#portal)
- [Using the Cockpit API](#api)


<a id="portal"></a>
### Using the Cockpit Portal

See the [Getting started with blueprints](../../Getting_started_with_blueprints/Getting_started_with_blueprints.md) section.


<a id="api"></a>
### Using the Cockpit API

In order to use the Cockpit API you first need to obtain an JWT, as documented in the section about [how to get a JWT](../Get_JWT/Get_JWT.md).

Once you got the JWT:

```
JWT="..."
BASE_URL="<IP-address>"
AYS_PORT="5000"
curl -X GET \
     -H "Authorization: bearer $JWT"  \
     https://$BASE_URL:$AYS_PORT/ays/repository
```

The `AYS_PORT` typically is 5000 and can be configured in `/optvar/cfg/cockpit_api/config.toml`.

Also see the section about the [API Console](../../API_Console/API_Console.md)
