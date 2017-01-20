## How to create a virtual machine

For creating a virtual machine use the **node.ovc** actor template, available here: https://github.com/Jumpscale/ays_jumpscale8/tree/master/templates/nodes/node.ovc

You first will need to create a virtual datacenter, as documented in [How to create a VDC](../Create_VDC/Create_VDC.md).

Then use the following blueprint for creating a new vm `myvm` in the vdc `myvdc`:

```
sshkey__main:

node.ovc__myvm:
  vdc: myvdc
  bootdisk.size: 20
  memory: 1
  os.image: 'Ubuntu 16.04 x64'
  sshkey: main

actions:
  - action: install
```
