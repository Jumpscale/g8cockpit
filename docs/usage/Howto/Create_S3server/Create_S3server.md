## How to create a S3 server

Steps:

- [Review the blueprint](#review-blueprint)
- [Put blueprint in a JSON file](#json-file)
- [Create a new repository (optionally)](#create-repository)
- [Send the blueprint to the Cockpit](#send-blueprint)
- [Execute the blueprint](#execute-blueprint)
- [Create a run](#create-run)
- [Check result](#check-result)
- [Test using s3cmd](#s3cmd-test)


<a id="review-blueprint"></a>
### Review the blueprint

Here's the blueprint:

```
g8client__{environment}:
  url: '{url}'
  login: '{login}'
  password: '{password}'
  account: '{account}'

vdc__{vdc-name}:
  g8client: '{environment}'
  account: '{account}'
  location: '{location}'

sshkey__{sshkey-name}:

disk.ovc__{disk-name}:
  size: {size}

s3__{s3server}:
  vdc: {vdc-name}
  sshkey: '{sshkey-name}''
  disk:
    - '{disk-name}'
  hostprefix: 'host-prefix'
  key.access: '{access}'
  key.secret: '{secret}'
  enablehttps: '{True | False}'

actions:
  - action: 'install'
```

Values:

- `{environment}`: environment name for referencing elsewhere in the same blueprint or other blueprint in the repository
- `{url}`: URL to to the G8 environment, e.g. `gig.demo.greenitglobe.com`
- `{login}`: username on the targeted G8 environment
- `{password}`: password for the username
- `{account}`: account on the targeted G8 environment used for the S3 server
- `{vdc-name}`: name of the VDC that will be created for the S3 server, and if a VDC with the specified name already exists then that VDC will be used
- `{location}`: location where the VDC needs to be created
- `{sshkey-name}`: name of the SSH key that will be created
- `{disk-name}`: name of the disk that will be created; you ca create multiple disks
- `{size}`: disk size in GB, for more details see
- `{hostprefix}`: the first part in your app URL, i.e `hostprefix` in the FQDN `hostprefix-machinedecimalip.gigapps.io`; the remaining part of the FQDN will be calculated, for more information see https://github.com/0-complexity/ipdns
- `{key.access}`: S3 access key (username); will be auto-generated when not set  
- `{key.secret}`: S3 access secret (password); will be auto-generated when not set
- `{enablehttps}`: to enable https; when omitted will default to False


<a id="json-file"></a>
### Put blueprint in a JSON file

Let's first put the blueprint in JSON file:

```
vi s3server.json
```

Copy/paste:

```json
{"name":"s3.yaml","content":"g8client__cl:\n  url: 'uk-g8-1.demo.greenitglobe.com'\n  login: 'cockpit'\n  password: 'cockpit12345'\n  account: 'Account of Yves'\n\nvdc__vdc4s3:\n  g8client: cl\n  account: 'Account of Yves'\n  location: 'uk-g8-1'\n\nsshkey__main:\n\ndisk.ovc__disk1:\n  size: 1000\n\ns3__s3server:\n  vdc: vdc4s3\n  sshkey: main\n  disk:\n    - 'disk1'\n  hostprefix: 'mys3'\n  key.access: 'access'\n  key.secret: 'secret'\n\nactions:\n  - action: 'install'"}
```

<a id="create-repository"></a>
### Create a new repository (optionally)

Create a new repository :

```
curl -X POST -H "Authorization: bearer $JWT$" -H "Content-Type: application/json" -d '{"name":"yves01", "git_url":"git@github.com:yveskerwyn/cockpit_repo_yves.git"}' http://{address}:5000/ays/repository | python -m json.tool
```

Notice the pipe to `python -m json.tool` in order to display the returned JSON in a readable format.

<a id="send-blueprint"></a>
### Send the blueprint to the Cockpit

Sending the blueprint to the Cockpit using `curl`:

```
curl -X POST -H "Authorization: bearer $JWT$" -H "Content-Type: application/json" -d @s3server.json http://85.255.197.77:5000/ays/repository/yves01/blueprint | python -m json.tool
```


<a id="execute-blueprint"></a>
### Execute the blueprint

Again using `curl`:

```
curl -X POST -H "Authorization: bearer $JWT$" http://{address}:5000/ays/repository/yves01/blueprint/s3.yaml | python -m json.tool
```

<a id="create-run"></a>
### Create a run

Using curl:

```
curl -X POST -H "Authorization: bearer $JWT$" http://{address}:5000/ays/repository/yves01/aysrun | python -m json.tool
```

<a id="check-result"></a>
### Check result

You can check the result in three ways:

- [Cockpit Portal](#cockpit-portal)
- [JumpScale Interactice Shell](#js-shell)
- [Cockpit-API](#cockpit-API)

All discussed below.


<a id="cockpit-portal"></a>
### Check result via the Cockpit Portal

In the **Cockpit** go to **Services** and select the `app` service of the `scalitity` actor:

![](domain.png)

Notice the value for `domain` which you will need in the configuration of `s3cmd` here below.

This domain name is generated using **ipdns**, a stateless DNS server, see: https://github.com/0-complexity/ipdns


<a id="js-shell"></a>
### Check result via the JumpScale Shell

The same information can be retrieved using `js`, with the repository directory as current directory:

```python
In [1]: repo = j.atyourservice.get()

In [2]: scalityapp = repo.serviceGet('scality', 'app')

In [3]: scalityapp.model.data
Out[3]: <schema_f9020c5a81a2021c_capnp:Schema builder (os = "app", domain = "mys3-1442825545.gigapps.io", storageData = "/data/data", storageMeta = "/data/meta", keyAccess = "access", keySecret = "secret")>
```


<a id="cockpit-api"></a>
### Check result via the Cockpit API

Here's how using curl:

```
curl -X GET -H "Authorization: bearer $JWT$" -H "Content-Type: application/json" http://{address}:5000/ays/repository/{repository-name}/service/s3/{actor-instance-name} | python -m json.tool
```

The JSON result will include all details, including the `fqdn`, `keyAcces`, and `keySecret`:

```
...
"enablehttps": false,
"fqdn": "mys3-1442825551.gigapps.io",
"hostprefix": "mys3",
"image": "Ubuntu 16.04 x64",
"keyAccess": "access",
"keySecret": "secret",
"sshkey": "main",
"vdc": "vdc4s3"
...
```

<a id="s3cmd-test"></a>
###  Test using s3cmd

Now let's test the S3 server using [s3cmd](http://s3tools.org/s3cmd-howto).

On your machine first thing to do is updating the content of `~/.s3cfg`, basically replacing everything with:

```
[default]
access_key = accessKey1
secret_key = verySecretKey1

host_base = mys3-1442825545.gigapps.io
host_bucket = mys3-1442825545.gigapps.io

signature_v2 = True
use_https = False
```

Make sure you changed the values of `host_base` and `host_bucket` to the value you got for `domain` in the **Cockpit** or by executing `js`, as explained [above](#check-result).

Once done, you can use start creating a bucket with `s3cmd mb` and use `s3cmd put` and `s3cmd get` to test the S3 server:

```
s3cmd ls
s3cmd mb s3://yves01
vi test
s3cmd put test s3://yves01
s3cmd get s3://yves01/test test2
cat test2
```
