## Installing a Cockpit in Development Mode using JumpScale Cuisine

On a machine with JumpScale preinstalled, as documented [here](https://gig.gitbooks.io/jumpscale-core8/content/Installation/JSDevelopment.html), open the JumpScale interactive shell:

```
js
```

And issue the following two commands to get your Cockpit up and running **locally** in development mode:

```
cuisine = j.tools.cuisine.local
cuisine.solutions.cockpit.install_all_in_one(start={True|False}, branch='8.1.1', reset={True|False}, ip='localhost|{ip-address}')
```

With the parameters:

- `start` (True|False) you control wether the Cockpit will start automatically once installed
- `branch` you specify the Git repository branch you want to install from
- `reset` (True|False) you control wether also the portal needs to be reinstalled
- `ip` ('localhost'|{ip-address}) you set the IP address on which the REST API will be available for remote interactions; if you specify `localhost` the REST API will only be available locally


Alternatively you can also get your Cockpit up and running in development mode, locally or on a **remote** machine by using an executor:

```
executor = j.tools.executor.getSSHBased(addr='localhost|{ip-address}', port={port-number}, login='{username}', passwd=None|'{password}', debug={True|False}, allow_agent=True, look_for_keys=True, timeout=5, usecache=True, passphrase=None, key_filename=None)
cuisine = j.tools.cuisine.get(executor)
cuisine.solutions.cockpit.install_all_in_one(start=True, branch='8.1.1', reset=True, ip='localhost}|{ip-address}')
```

As a result you'll have your Cockpit running in development mode, and listing to following ports:

- Port 82, for the Cockpit Portal
- Port 5000, for the Cockpit REST API

If you installed the Cockpit on a G8 hosted virtual machine, you will want to configure port forwards to make it available for remote interactions.
