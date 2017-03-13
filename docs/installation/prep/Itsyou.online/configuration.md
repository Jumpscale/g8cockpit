# How to Configure ItsYou.online Integration

## Enable ItsYou.online integration

First make sure that you setup the required ItsYou.online organizations as documented in [Setup the ItsYou.online Organizations](Itsyou.online).

Update `/optvar/cfg/portals/main/config.hrd` as follows:

- Set `param.cfg.production           = True`
- Set `param.cfg.force_oauth_instance = 'ItsYou.online'`
- Change `param.cfg.client_id         = '{client-id}'`
- Change `param.cfg.client_secret     = '{client-secret}'`
- Set `param.cfg.redirect_url         = 'https://{cockpit-base-address}/restmachine/system/oauth/authorize'`
- Set `param.cfg.organization         = '{organization}'`

Update `/optvar/cfg/cockpit_api/config.toml` as follows:

- Remove `production = False` or set to `True`
- Set `organization = "{organization}"`
- Set `redirect_uri = "https://cockpit-base-address/api/oauth/callback"`
- Set `client_secret = "{client-secret}"`
- Set `client_id = "{organization_id}"`
- Set `jwt_key = "{JWT-for-ItsYou.online}"`


Values:

- **{client-id}**: name of the organization as set in ItsYou.online, typically the company/organization for which you are setting up the Cockpit; in order for a user to be able to use the Cockpit he doesn't need be owner or member of this organization
- **{client-secret}**: the client secret that goes with the `{client-id}` of the organization for which the Cockpit is setup
- **{cockpit-base-address}**: the IP address of domain name (FQDN) on which the Cockpit is active, e.g. `mycockpit.aydo2.com`
- **{organization}**: name of the organization as set in ItsYou.online, to which a Cockpit user needs be member or owner; can be the same organization as specified with `{client-id}`, but can also be different
- **{JWT-for-ItsYou.online}**: set it to the following string:
  ```
  -----BEGIN PUBLIC KEY-----
  MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n2
  7MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny6
  6+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv
  -----END PUBLIC KEY-----
  ```

Restart the Cockpit API (`cockpit_main`) and the Portal (`portal`):

```
systemctl restart cockpit_main
systemctl restart portal
```

## Diable ItsYou.online integration


Update `/optvar/cfg/portals/main/config.hrd` as follows:

- Set `param.cfg.production           = False`

Update `/optvar/cfg/cockpit_api/config.toml` as follows:

- Set `production = False`
