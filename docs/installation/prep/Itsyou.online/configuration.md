# How to configure cockpit to work with/without itsyou.online
- the organization and client_id are the organization name that you created in itsyou.online
- the client_secret, you can get it by creating an `API ACCESS Key` in ityou.online under organization `settings` and configure the callbackurl like the following
![](api.png)



## Change cockpit to use itsyou.online if it is in dev mode
- Open /optvar/cfg/portals/main/config.hrd
- set `param.cfg.production           = True`
- set `param.cfg.force_oauth_instance = 'itsyou.online'`
- change `param.cfg.client_id            = 'JSPortal'` to your Organinzation ID that is in itsyou.online
- change `param.cfg.client_secret        = 'MT*************************************pq'` to the equivalent one in itsyou.online
- set `param.cfg.redirect_url         = 'https://testcockpit.aydo2.com/restmachine/system/oauth/authorize'` to the correct cockpit url or use IP
- set `param.cfg.organization         = 'JSPortal'` set to organization ID
- open /optvar/cfg/cockpit_api/config.toml
- if you have `production = False` remove it or set to `True`
- set `organization = "cockpitorg1"` to be the organization you created in itsyou.online
- set `redirect_uri = "https://testcockpit.aydo2.com/api/oauth/callback"`
- set `client_secret = "<client_secret_from_itsyou.online>"`
- set `client_id = "<organization_id>"`
- set `jwt_key = "<JWT_for_itsyou.online>"`

## set cockpit to `NOT` use itsyou.online
- Open /optvar/cfg/portals/main/config.hrd
- set `param.cfg.production           = False`
- - open /optvar/cfg/cockpit_api/config.toml
- set `production = False`
