# How to Create a New Repository

You can create a repository in multiple ways:

- [Using the AYS CLI client](#cli)
- [Using the AYS/Cockpit API](#api)
- [In the Cockpit Portal](#portal)


<a id="cli"></a>
## Using the AYS CLI client

```
REPO_NAME="..."
GIT_URL="https://github.com/<user>/<repository-name>"
ays repo create -n $REPO_NAME -g $GIT_URL
```

As a result a new repository will be created:
```
cd REPO_NAME
```

It contains two empty directories:
- `blueprints`
- `actorTemplates`

Once you add your first blueprint, and execute it, two more directories will be created:

- `actors`
- `services`

See [How to Execute Blueprints](../Execute_blueprint/Execute_blueprint.md) for more details on this.

<a id="api"></a>
## Using the AYS API

In order to use the Cockpit API you first need to obtain an JWT, as documented in the section about [how to get a JWT](../Get_JWT/Get_JWT.md).

Once you got the JWT:

```
JWT="..."
REPO_NAME="..."
GIT_URL="https://github.com/user/reponame"
BASE_URL="<IP-address>"
AYS_PORT="5000"
curl -H "Authorization: bearer $JWT" \
     -H "Content-Type: application/json" \
     -d '{"name":"'$REPO_NAME'", "git_url": "'$GIT_URL'"}' \
     https://$BASE_URL:$AYS_PORT/ays/repository
```

In the **API Console**:

![](create-repository.png)

For more information about the **API Console** go to the section about the [API Console](../../API_Console/API_Console.md).


<a id="portal"></a>
## Using the Cockpit Portal

See the [Getting started with blueprints](../../Getting_started_with_blueprints/getting_started_with_blueprints.md) section.
