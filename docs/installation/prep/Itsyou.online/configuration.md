# How to Configure ItsYou.online Integration

Below we discuss how to:

- [Enable ItsYou.online integration](#enable)
- [Diable ItsYou.online integration](#disable)

In both cases a restart of the of the **Cockpit API** (`cockpit_main`) and the **Portal** (`portal`) is required:

```
systemctl restart cockpit_main
systemctl restart portal
```


<a id="enable"></a>
## Enable ItsYou.online integration

First make sure that you setup the required ItsYou.online organizations as documented in [Setup the ItsYou.online Organizations](Itsyou.online).

You will have to update to files:
- `/optvar/cfg/portals/main/config.hrd` for configuring the **Cockpit Portal**
- `/optvar/cfg/cockpit_api/config.toml` for configuring the **Cockpit API**

Update `/optvar/cfg/portals/main/config.hrd` as follows:

- Set `param.cfg.production           = true`
- Set `param.cfg.client_scope         = 'user:email:main,user:memberof:{organization}'`
- Set `param.cfg.force_oauth_instance = 'itsyou.online'`
- Change `param.cfg.client_id         = '{client-id}'`
- Change `param.cfg.client_secret     = '{client-secret}'`
- Set `param.cfg.redirect_url         = 'http://{cockpit-base-address}/restmachine/system/oauth/authorize'`
- Add `param.cfg.organization         = '{organization}'`
- Add `param.cfg.oauth.default_groups = 'admin', 'user',`
- Set `param.cfg.client_user_info_url = 'https://itsyou.online/api/users/'`
- Set `param.cfg.token_url            = 'https://itsyou.online/v1/oauth/access_token'`


Update `/optvar/cfg/cockpit_api/config.toml` as follows:

- Remove `prod = false` or set to `true`
- Set `organization = "{organization}"`
- Set `redirect_uri = "http://{cockpit-base-address}/api/oauth/callback"`
- Set `client_secret = "{client-secret}"`
- Set `client_id = "{organization}"`
- Set `jwt_key = "-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n2\n7MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny6\n6+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv\n-----END PUBLIC KEY-----\n"`


Values:

- **{client-id}**: name of the organization as set in ItsYou.online, typically the company/organization for which you are setting up the Cockpit; in order for a user to be able to use the Cockpit he doesn't need be owner or member of this organization
- **{client-secret}**: the client secret that goes with the `{client-id}` of the organization for which the Cockpit is setup
- **{cockpit-base-address}**: the IP address of domain name (FQDN) on which the Cockpit is active, e.g. `mycockpit.aydo2.com`
- **{organization}**: name of the organization as set in ItsYou.online, to which a Cockpit user needs be member or owner; can be the same organization as specified with `{client-id}`, but can also be different


<a id="disable"></a>
## Disable ItsYou.online integration

Update `/optvar/cfg/portals/main/config.hrd` as follows:

- Set `param.cfg.production           = false`

Update `/optvar/cfg/cockpit_api/config.toml` as follows:

- Set `prod = false`
