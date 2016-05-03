
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

- @todo spec format (see jumpscale)


#### alarm

- @todo spec format


#### telegram

- @todo spec format

#### email

- files stored in CuisineStor enabled over http site with browsing off
- body text or markdown
	- if html incoming try to convert to markdown as good as possible 
- recognise if markdown (e.g. if certain specific markdown elements there)
- can store files

example with files



```yaml
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

## CuisineStor

- see [specs cuisine stor](https://github.com/Jumpscale/jumpscale_core8/blob/77e9a2c6685783dd296c93b68411f41d58582708/lib/JumpScale/tools/cuisine/CuisineStor.py)
	- check newest version this is 1 specific commit 
