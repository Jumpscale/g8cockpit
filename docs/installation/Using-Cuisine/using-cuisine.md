## Installing a Cockpit in Development Mode using JumpScale Cuisine

On a machine with JumpScale preinstalled, as documented [here](https://gig.gitbooks.io/jumpscale-core8/content/Installation/JSDevelopment.html), open the JumpScale interactive shell:

```
js
```

And issue the following two commands to get your Cockpit up and running **locally** in development mode:

```
cuisine = j.tools.cuisine.local
cuisine.solutions.cockpit.install(start={True|False}, branch='8.1.1', reset={True|False}, ip='localhost|{ip-address}')


cuisine.solutions.cockpit.install(start=True, branch='8.2.0', reset=False, ip='localhost', production=False, client_id='', ays_secret='', portal_secret='', organization='')

and more parameters now

Reem Khamis, [17 May 2017, 14:21]:
Yes
```

Parameters:

- `start`: specifies (True|False) wether the Cockpit will start automatically once installed
- `branch`: specifies the Git repository branch you want to install from
- `reset`: controls (True|False) wether the [JumpScale Portal](https://github.com/Jumpscale/jumpscale_portal8) needs to be reinstalled
- `ip`: sets the IP address ('localhost'|{ip-address}) on which the REST API will be available for remote interactions; if you specify `localhost` the REST API will only be available locally
- `production`:
- `client_id`: name (OAuth client_id) of the ItsYou.online organization for which you are setting up the Cockpit; in order for a user to be able to use the Cockpit he doesn't need be owner or member of this organization
- `portal_secret`: API access key (OAuth client secret) created for the organization identified with `{client-id}` (the organization for which the Cockpit is setup), this key will be used in the Authorization Code grant type flow when the user logs in the Cockpit Portal in order to authenticate itself
- `ays_secret`: API access key (OAuth client secret) created for the organization identified with `{client-id}` (the organization for which the Cockpit is setup), this key will be used in the Client Credentials Code grant type flow when AYS wants to operate on behalf of the organization for which the Cockpit was setup
- `organization`: name (OAuth client_id) of the ItsYou.online organization of which a Cockpit user needs be member; can be the same organization as specified with `{client-id}`, but can also be different


- **{client-id}**: name of the organization as set in ItsYou.online, typically the company/organization for which you are setting up the Cockpit; in order for a user to be able to use the Cockpit he doesn't need be owner or member of this organization
- **{client-secret}**: the client secret that goes with the `{client-id}` of the organization for which the Cockpit is setup
- **{cockpit-base-address}**: the IP address of domain name (FQDN) on which the Cockpit is active, e.g. `mycockpit.aydo2.com`
- **{organization}**: name of the organization as set in ItsYou.online, of which a Cockpit user needs be member or owner; can be the same organization as specified with `{client-id}`, but can also be different


Alternatively you can also get your Cockpit up and running in development mode, locally or on a **remote** machine by using an executor:

```
executor = j.tools.executor.getSSHBased(addr='localhost|{ip-address}', port={port-number}, login='{username}', passwd=None|'{password}', debug={True|False}, allow_agent=True, look_for_keys=True, timeout=5, usecache=True, passphrase=None, key_filename=None)
cuisine = j.tools.cuisine.get(executor)
cuisine.solutions.cockpit.install_all_in_one(start=True, branch='8.1.1', reset=True, ip='localhost}|{ip-address}')
```

The IP address you specify can always be updated, which requires updates in two files:

- In `/opt/jumpscale8/apps/ays_api/ays_api/apidocs/api.raml` change the value for `baseUri` in the `[API]` section
- In `/opt/jumpscale8/apps/portals/main/base/AYS81/.space/nav.wiki` change the value for `AYS API`

As a result you'll have your Cockpit running in development mode, and listing to following ports:

- Port 82, for the **Cockpit Portal**
- Port 5000, for the **Cockpit REST API**

If you installed the Cockpit on a G8 hosted virtual machine, you will want to configure port forwards to make it available for remote interactions.

There are two Cockpit configuration files:

- Portal configuration: `/optvar/cfg/portals/main/config.hrd`
- Cockpit API configuration: `/optvar/cfg/cockpit_api/config.toml`

By default JumpScale Cuisine installs the Cockpit with ItsYou.online integration disabled. You can manually enable this OAuth integration as discussed in [How to Configure ItsYou.online Integration](../prep/Itsyou.online/configuration.md).

When changing configuration make sure to restart the **Cockpit API** (`cockpit_main`), **Cockpit Engine** (`cockpit_daemon_main`) and/or the **Portal** (`portal`):

```
systemctl restart cockpit_main
systemctl restart cockpit_daemon_main
systemctl restart portal
```


Use the following commands to check the status:

```
systemctl status cockpit_daemon_main
systemctl status cockpit_main
systemctl status portal
```

Also see: https://github.com/Jumpscale/jumpscale_core8/blob/8.1.1/docs/AYS/configuration.md
