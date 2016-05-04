
## gevent based robot

### requirements

- smtp server (send/receive)
- rest server with autodocumentation
	- integrate swagger or raml javascript frontend
- telegram robot
- ays robot
- all in 1 gevent based server  


### events

- types of events
	- incoming email
	- incoming telegram message
	- monitoring alarm
	- eco (jumpscale error condition)
	- generic (tags, ...) to work in more generic way e.g. conversion from github webhooks

example message formats in yaml


### core objects

make sure they exist in our j.data.models...
and we can use them without mongodb !!!!! if possible, if not lets skip if for now

#### eco

```yaml
type: 'eco'
guid : '762d6f24-8b50-4e46-8cb6-fa6d0f56f1fd'
gid: 1
nid: 10
pid: 239
app_name: 'myapp'
eco_type: 'BUG'
state: 'NEW'
error_msg: 'error internal'
error_pub: 'Something went wrong, sorry'
category: 'eco.category'
func_name: 'hello'
func_filename: 'main.py'
line_nbr: 23
code: |
from JumpScale import j
print('hello world')
backtrace: |
backtrace here
extra: 'extra detail'
last_time: 1462275396
close_time: 1462275496
occurence: 2
tags: 'list of tags here'
```


#### alarm

```yaml
type: 'alarm'
service: 'myservice!instance'
method: 'monitor'
msg: 'Something wrong happend'
epoch: 1462275396
```


#### telegram
Telegram can send different type of event but we try to keep the event created generic.
Based on the io and the action, the subscriber can expect different data in the 'args' dictionnary.

e.g. repo creation:
```yaml
type: telegram
io: input
action: repo.create
args:
 name:'env du-conv2'
```
e.g. blueprint creation:
```yaml
type: telegram
io: input
action: bp.create
args:
 name:'1_nodes.yaml'
 content: |
 here the content of the blueprint
```
e.g. service action execution:
```yaml
type: telegram
io: input
action: service.execute
args:
 name:'node!cpu1'
 action: 'monitor'
```
#### email

- files stored in CuisineStor enabled over http site with browsing off
- body text or markdown
	- if html incoming try to convert to markdown as good as possible 
- recognise if markdown (e.g. if certain specific markdown elements there)
- can store files

example with files



```yaml
type: email
body: '
  this is a test

  can be multiple lines

  '
bodytype: md
attachments: {"aname.doc":"https://stor.something.com:8080/myspacename/aa/bb/aabbccddeeffgghh",...}
cc: []
from: kristof@incubaid.com
subject: a subject
```

## Pub/Sub mechanism 
Pub/Sub is done over redis.
Any component of the cockpit can publisher of event. (SMTP server, telegram robot, ays robot, REST server)  
Only Telegram robot and AYS robot and AYS services can be subscriber of events.  

It exists one topic by event type:
- ckpt.email
- ckpt.telegram
- ckpt.alarm
- ckpt.eco
- ckpt.generic

AYS robot subscribe to all event and forward the event to the correct AYS service.  
AYS services describe which event they are interested in in the `service.hrd` file  
```
events.$event-type = 
	$action-name,
	$action-name,
```
e.g : 
```
events.emai = 
	notify,
	escalate,
```
This service ask to subscribe to the events from SMTP server. The method notify and escalate will be executed with as first argument the payload of the message.

## CuisineStor

- see [specs cuisine stor](https://github.com/Jumpscale/jumpscale_core8/blob/77e9a2c6685783dd296c93b68411f41d58582708/lib/JumpScale/tools/cuisine/CuisineStor.py)
	- check newest version this is 1 specific commit 
