
## How to get yourself a cockpit

### On a G8 enabled cloud using our robot
Using telegram, you can talk to `....(name to be defined)`. This is a robot that will guide you trough the step of deploying a new cockpit


### Using AtYourService
You can deploy a new cockpit using AYS.  
Use the [blueprint](../scripts/ays_cockpit/1_cockpit.yaml) located in the script folder of this repo.
Update the blueprint parameters with your data.   
Then execute the blueprint:
```sh
cd scripts
ays init
ays install
```
