## How to create a blueprint

You can create a blueprint in three ways:

- [Using the Telegram Chatbot](#telegram)
- [In the Cockpit Portal](#portal)
- [Using the Cockpit API](#api)
- [At the CLI](#cli)

<a id="telegram"></a>
### Using the Telegram Chatbot

@todo


<a id="portal"></a>
### Using the Cockpit Portal

See the [Getting started with blueprints](../../Getting_started_with_blueprints/Getting_started_with_blueprints.md) section.


<a id="api"></a>
### Using the Cockpit API

In order to use the Cockpit API you first need to obtain an JWT, as documented in the section about [how to get a JWT](../Get_JWT/Get_JWT.md).

Once you got the JWT, you can create a blueprint, for instance here below for creating a new user "silke" on gig.demo.greenitglobe.com:

```
curl -H "Authorization: bearer JWT"  /
     -H "Content-Type: application/json" /
     -d '{"name":"test-blueprint","content":"g8client__gig:\n  g8.url: 'gig.demo.greenitglobe.com'\n  g8.login: 'xyz'\n  g8.password: '***'\n  g8.account: 'Account of Yves'\n\novc_user__user1:\n  g8.client.name: 'gig'\n  username: 'silke'\n  email: 'silkevansteenkiste@msn.com'\n  provider: 'itsyouonline'"}'
     https://BASE_URL/api/ays/repository/
```

Also see the section about the [API Console](../../API_Console/API_Console.md)

<a id="cli"></a>
### At the CLI

@todo

Also see [How to add a user](../Add_user/Add_user.md).
