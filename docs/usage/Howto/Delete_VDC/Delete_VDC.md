## How to delete a VDC

For deleting a virtual datacenter (VDC) use the **vdc** actor template, available here: https://github.com/Jumpscale/ays_jumpscale8/tree/master/templates/ovc/vdc


In case the actor is already loaded in the AYS repository simply use the following blueprint:

```
actions:
  - action uninstall
    actor: vdc
    service: {vdc-name}
```

If not:

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
  - action: uninstall
    actor: vdc
    service: {vdc-name}
```

>> Deleting the VDC actor will not automatically call the uninstall() action.
