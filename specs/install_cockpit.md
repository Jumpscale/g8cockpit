

# this repo is
- jumpscale install script to get going in interactive way with cockpit
- ays repo for templates to do with deploying a cockpit
- default portal for mgmt of a cloud env (jsportal based)
- example blueprints
- example portals
- documentation: explaining how to get going with a cockpit

# defs

## cockpit repo

- ays repo for cloud deployment of customer + blueprints
- has copy of portal (which can be freely modified)
- example scripts
- example ays templates which are meant to be changed
- example blueprints

## cockpit machine

- what is in there
  - has the cockpit repo checked out
  - has telegram ays robot
  - has mongodb
  - has agentcontroller
  - has portal
  - influxdb
  - caddy (generate non official ssl certificate)
- install by using our full build process (through cuisine) (WILL BE SANDBOX LATER)
- based on ubuntu 15.10

# todo

## install script

- start from machine with js8 (sandbox or development mode)
- ask github repo url (customer should use ssh key) = is the cockpit repo which will be used
- we copy relevant content in this repo
- ask interactive details for connection to an openvcloud (e.g. ms1)
  - we configure that connection in ays (in the cockpit repo)
  - we check the connection if it is working
- ask interactive details for skydns (for now prob admin account)
  - we configure that connection in ays (in the cockpit repo)
  - we check the connection if it is working
- ask which ssh key to be used or generate new one
  - ask from agent as well if loaded
  - is ssh key to get access to cockpit
- commit/push changes to cockpit repo
- we ask for space to use, in which we will deploy the cockpit machine (will take upto 20 min)
- go inside the cockpit machine (ssh)
  - checkout cockpit repo
  - ask admin passwd: 
      - configure portal for this passwd
  - configure mongodb, influxdb to use all std passwd's which are used by portal
      - print the passwds used
  - authorize ssh key to cockpit machine (so local user can get to it seamless)
  - get ip address of vdc router, configure ssh portforward to the cockpit, print the ip address
- ask for cockpit name
  - see if $cockpitname.cockpit.aydo.com is free, if yes configure in skydns 
  - print the url to user, so he knows how to get to cockpit ip address (which is VDC ip address)
  - remember name in ays
- make sure the portforward script is inside the cockpit repo
- use the cockpit name to create a telegram robot (or ask the name from user when already created in advance, whatever is easiest)
  - deploy the robot
  
## portforward script to get access to cockpit
  - in background start ssh portforward session 
    - localhost: 2080 to get to portal
    - localhost: 2090 for controller
    - localhost: 2091 for redis
    - localhost: 2092 for influxdb
    - localhost: 2093 for mongodb
  - use ays info to know which cockpit ip addr to go to
  
  
