## How to activate an auto-snapshotting policy

For activating an auto-snapshotting policy for a give virtual datacenter use the **autosnapshotting** actor template, available here: https://github.com/Jumpscale/ays_jumpscale8/tree/master/templates/ovc/autosnapshotting

For the example below we used a virtual datacenter `myvdc` with one virtual machine `myvm` created with the below blueprint:

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

sshkey__main:

node.ovc__myvm:
  vdc: myvdc
  bootdisk.size: 20
  memory: 2
  os.image: 'Ubuntu 16.04 x64'
  sshkey: main

actions:
  - action: install
```

For a given virtual datacenter you can activate auto-snapshotting by sending following blueprint:

```
autosnapshotting__mysnapshotting:
  snapshotInterval: 1h
  cleanupInterval: 1d
  retention: 3d
  vdc: myvdc

actions:
  - action: install
```
