# How to Create a Blueprints

You can create a blueprint in multiple ways:

- [At the CLI](#cli)
- [Using the Cockpit API](#api)
- [In the Cockpit Portal](#portal)

All are discussed here below.

Make sure to validate your blueprint first to have valid YAML format using a tool like [YAML Lint](http://www.yamllint.com/).

<a id="cli"></a>
## At the CLI

In order to creating a blueprint you need to have repository, creating repositories is discussed in [How to Create Repositories](../Create_repository/Create_repository.md).

```
vi blueprints/blueprint.yaml
```


<a id="api"></a>
## Using the Cockpit API

In order to use the Cockpit API you first need to obtain an JWT, as documented in the section about [how to get a JWT](../Get_JWT/Get_JWT.md).

Once you got the JWT, you can create a blueprint, for instance here below for creating a new user "mike" on gig.demo.greenitglobe.com:

```
curl -H "Authorization: bearer JWT"  /
     -H "Content-Type: application/json" /
     -d '{"name":"user1.yaml","content":"ovc_user__user1:\n  g8.client.name: 'gig'\n  username: 'mike'\n  email: 'mike@gmail.com'\n  provider: 'itsyouonline'"}'
     https://BASE_URL/ays/repository/REPO_NAME/blueprint/
```

> Note that the above blueprint will not create the user. Two more steps are are required for that, first execute the blueprint and then install the user, respectively documented in the sections [How to execute a blueprint](../Execute_blueprint/Execute_blueprint.md) and [How to install a service](Install_service/Install_service.md).

Also see the section about the [API Console](../../API_Console/API_Console.md)

<a id="portal"></a>
## Using the Cockpit Portal

See the [Getting started with blueprints](../../Getting_started_with_blueprints/getting_started_with_blueprints.md) section.
