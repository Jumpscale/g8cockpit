# How to Grant User Access to a VDC

For granting a user access rights to a virtual datacenter (VDC) you will use a `vdc` blueprint, actually the same blueprint you use for creating a new VDC, as documented in [How to Create a VDC](../Create_VDC/Create_VDC.md).

The `vdc` blueprint is defined in the `vdc` AYS template, available here: https://github.com/Jumpscale/ays_jumpscale8/tree/master/templates/ovc/vdc

- [Blueprint](#blueprint)

<a id="blueprint"></a>
## Blueprint

```yaml
vdc__{vdc-name}:
  g8client: '{environment}'
  account: '{account}'

  uservdc:
    - `{username_of_new_user}`
    - `{username_of_other_user}`
```

The above blueprint requires that `{environment}` and both the `{username_of_new_user}` and `{username_of_other_user}` are already defined in another blueprint in the same AYS repository. If not the case you can add them into the same blueprint:

```yaml
g8client__{environment}:
  url: '{url}'
  login: '{login}'
  password: '{password}'
  account: '{account}'

uservdc__{username_of_new_user}:
  g8client: '{environment}'
  email: '{email1}'
  provider: 'itsyouonline'

uservdc__{username_of_other_user}:
  g8client: '{environment}'
  email: '{email2}'
  provider: 'itsyouonline'
```

The second user in the blueprint, `{username_of_other_user}`, represents any other user you want to grant access to the VDC, in particular the users that already have access rights. If you don't include them in the blueprint does users will have their access rights revoked.

```
vi blueprints/gen.yaml
```

```
g8client__gen:
    url: 'du-conv-2.demo.greenitglobe.com'
    login: 'cockpit'
    password: 'Eiqueeyohlei4soo'
```

```
ays blueprint blueprints/gen.yaml
```

```
vi blueprints/vdc.yaml
```

```
vdc__yvesvdc22:
    description: 'cockpit vdc'
    g8client: 'gen'
    location: 'du-conv-2'
```

```
ays blueprint blueprints/vdc.yaml
```

```
vi blueprints/actions.yaml
```

```
actions:
  - action: install
```

```
ays blueprint actions.yaml
```

```
ays create run
```
