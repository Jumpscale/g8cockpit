
SIMPLE docker install with blueprint

```
vdcfarm_ms1:
    login: "something"
    passwd: "???"
    description: "my test farm for dockers"

vdc_uk2:
    location: "eu1"
    account : "operations"
    vdcfarm : "ms1"

dockerhost_demo2dh2:
    vdc : "uk2"
    mem: 8

docker_mydocker1:
    host: 'demo2dh'
    docker.hub: 'despiegk/astersik11_freepbx12_isymphonyv3'
    domain: 'demo.barcelona.aydo.com'
    mem: 0.2  #we can limit mem
    expose: 80-8080  #expose 80 on docker to 8080 on VDC router

```

remarks
- if no ssh keys used then create the std ssh key created by default on the cockpit machine for blueprints

result is
- cockpit machine deploys the blueprint & has ssh access to the dockers & dockerhost using ssh keys
- the main shellinabox running in cockpit machine gets configured to expose the console of the dockers & vm's
- caddy gets configured to expose that shellinabox with a unique link 
- print the links to the dockers & vm's in the telegram when used to launch such a blueprint
