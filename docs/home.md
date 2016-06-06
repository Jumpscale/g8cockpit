# JSCockpit

This repo contains all the materials related to JSCockpit:

- [JSCockpit code](../app)
- [Deployer bot](../deployer_bot)
- [Script to build the docker image of JSCockpit](../scripts/building.py)

Check the README in each component to have more detail.


### Generate Client for AYS REST API:
- Install go-raml : https://github.com/Jumpscale/go-raml#install
- Generate client code from raml specifications
```
go-raml client -l python --dir client --ramlfile jscockpit/ays_api/specifications/ays.raml
```
- Edit the client.py file and update the `BASE_URI`

#### How to use:
```python
jwt = "jwt from itsyou.online"
cl = Client()
cl.BASE_URI = 'https://mycockpit.com/api'
resp = cl.listRepositories(headers={"Authorization": "token " + jwt})
resp.json()
```

If you use JumpScale a client is available at `j.clients.cockpit`
