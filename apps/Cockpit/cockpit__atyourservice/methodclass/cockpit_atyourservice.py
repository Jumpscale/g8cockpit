from JumpScale import j
from JumpScale.portal.portal import exceptions
import jwt
from collections import OrderedDict


class cockpit_atyourservice(j.tools.code.classGetBase()):

    """
    gateway to atyourservice
    """

    def __init__(self):
        cockpit_cfg = j.portal.server.active.cfg.get('cockpit')
        self.base_url = "http://{host}:{port}".format(**cockpit_cfg)

    def get_client(self, **kwargs):
        session = kwargs['ctx'].env['beaker.session']
        jwttoken = session.get('jwt_token')
        if jwttoken:
            claims = jwt.decode(jwttoken, verify=False)
            # if jwt expire, we fore reloading of client
            # new jwt will be created it needed.
            if j.data.time.epoch >= claims['exp']:
                jwttoken = None

        if jwttoken is None:
            jwttoken = j.apps.system.oauthtoken.generateJwtToken(scope='', audience='', **kwargs)
            session['jwt_token'] = jwttoken
            session.save()
        return j.clients.cockpit.getClient(self.base_url, jwttoken)

    def cockpitUpdate(self, **kwargs):
        cl = self.get_client(**kwargs)
        return cl.updateCockpit()

    def addTemplateRepo(self, url, branch='master', **kwargs):
        """
        Add a new service template repository.
        param:url Service template repository URL
        param:branch Branch of the repo to use default:master
        result json
        """
        if url == '':
            raise exceptions.BadRequest("URL can't be empty")

        if not url.startswith('http'):
            raise exceptions.BadRequest("URL Format not valid. It should starts with http")

        if url.endswith('.git'):
            url = url[:-len('.git')]

        cl = self.get_client(**kwargs)

        try:
            resp = cl.addTemplateRepo(url=url, branch=branch)
        except j.exceptions.RuntimeError as e:
            raise exceptions.BadRequest(e.message)

        self.reload(**kwargs)

        return "Repository added"

    def listRepos(self, **kwargs):
        cl = self.get_client(**kwargs)
        repos = cl.listRepositories()
        repos = sorted(repos, key=lambda repo: repo['name'])
        return repos

    def listRuns(self, repository=None, **kwargs):
        """
        list all repository's runs
        param:repository in that repo will only be returned otherwise all runs
        result list of runids
        """
        cl = self.get_client(**kwargs)
        output_runs = dict()
        repos = self.listRepos(**kwargs)
        repos = [repository] if repository else [r['name']for r in repos]

        for aysrepo in repos:
            runs = cl.listRuns(repository=aysrepo)
            output_runs.update({aysrepo: runs})
        return output_runs

    def getSource(self, hash, repository, **kwargs):
        """
        param:repository where source is
        param: hash hash of source file
        result json of source
        """
        cl = self.get_client(**kwargs)
        source = cl.getSource(source=hash, repository=repository)
        return source

    def getHRD(self, hash, repository, **kwargs):
        """
        param:repository where source is
        param: hash hash of hrd file
        result json of hrd
        """
        cl = self.get_client(**kwargs)
        hrd = cl.getHRD(hrd=hash, repository=repository)
        return hrd

    def getRun(self, repository=None, runid=None, **kwargs):
        """
        get run
        param:repository
        param: runid
        result json of runinfo
        """
        cl = self.get_client(**kwargs)
        aysrun = cl.getRun(aysrun=runid, repository=repository)
        return aysrun

    def listServices(self, repository=None, role=None, templatename=None, **kwargs):
        """
        list all services
        param:name services in that base name will only be returned otherwise all names
        result json of {aysname:services}
        """
        cl = self.get_client(**kwargs)
        output_services = dict()
        repos = self.listRepos(**kwargs)
        repos = [repository] if repository else [r['name']for r in repos]

        for aysrepo in repos:
            services = cl.listServices(repository=aysrepo)
            # repo = j.atyourservice.repos[aysrepo]
            if role:
                output_services.update({aysrepo: {service['key']: service for service in services if service['role'] == role}})
            elif templatename:
                output_services.update({aysrepo: {service['key']: service for service in services if service['name'] == templatename}})
            else:
                output_services.update({aysrepo: services})
        return output_services

    def getService(self, repository, role, instance, **kwargs):
        cl = self.get_client(**kwargs)
        return cl.getServiceByInstance(instance, role, repository)

    def executeBlueprint(self, repository, blueprint='', role='', instance='', **kwargs):
        """
        execute blueprint
        param:name blueprints in that base name will only be returned otherwise all names
        result json
        """
        cl = self.get_client(**kwargs)
        role = '' if not role else role
        instance = '' if not instance else instance
        if not blueprint:
            blueprints = [bp['name'] for bp in self.listBlueprints(repository=repository, archived=False, **kwargs)[repository]]
        else:
            blueprints = [blueprint]
        try:
            for bp in blueprints:
                cl.executeBlueprint(repository=repository, blueprint=bp, role=role, instance=instance)
        except Exception as e:
            raise exceptions.BadRequest(str(e))

        msg = "blueprint%s\n %s \nexecuted" % ('s' if len(blueprints) > 1 else '', ','.join(blueprints))
        return msg

    def listBlueprints(self, repository=None, archived=True, **kwargs):
        """
        list all blueprints
        param:name blueprints in that base name will only be returned otherwise all names
        result json
        """
        cl = self.get_client(**kwargs)
        blueprints = OrderedDict()
        repos = self.listRepos(**kwargs)
        repos = [repository] if repository else [r['name']for r in repos]

        for aysrepo in repos:
            bps = cl.listBlueprints(repository=aysrepo, archived=archived)
            blueprints.update({aysrepo: bps})

        return blueprints

    def archiveBlueprint(self, repository, blueprint, **kwargs):
        """
        archive blueprint
        param:name blueprints in that base name will only be returned otherwise all names
        result json
        """
        cl = self.get_client(**kwargs)
        try:
            resp = cl.archiveBlueprint(repository=repository, blueprint=blueprint)
        except Exception as e:
            raise exceptions.BadRequest(str(e))
        return resp['msg']

    def restoreBlueprint(self, repository, blueprint, **kwargs):
        """
        list all blueprints
        param:name blueprints in that base name will only be returned otherwise all names
        result json
        """
        cl = self.get_client(**kwargs)
        try:
            resp = cl.restoreBlueprint(repository=repository, blueprint=blueprint)
        except Exception as e:
            raise exceptions.BadRequest(str(e))
        return resp['msg']

    def listTemplates(self, repository=None, **kwargs):
        """
        list all templates of a certain type
        result json
        """
        cl = self.get_client(**kwargs)
        templates = dict()
        repos = self.listRepos(**kwargs)
        repos = [repository] if repository else [r['name']for r in repos]

        for aysrepo in repos:
            tmpls = cl.listTemplates(repository=aysrepo)
            templates.update({aysrepo: tmpls})
        return templates

    def getTemplate(self, repository, template, **kwargs):
        """
        list all templates of a certain type
        result json
        """
        cl = self.get_client(**kwargs)
        return cl.getTemplate(repository=repository, template=template)

    def createRepo(self, name, **kwargs):
        cl = self.get_client(**kwargs)
        data = j.data.serializer.json.dumps({'name': name})
        resp = cl._client.createNewRepository(data=data)
        if resp.status_code != 200:
            ret = resp.json()
            ret['status_code'] = resp.status_code
            return ret
        return resp.json()

    def deleteRepo(self, repository, **kwargs):
        cl = self.get_client(**kwargs)
        resp = cl._client.deleteRepository(repository=repository)
        if resp.status_code != 204:
            ret = resp.json()
            ret['status_code'] = resp.status_code
            return ret
        return

    def init(self, repository, role='', instance='', force=False, **kwargs):
        cl = self.get_client(**kwargs)
        try:
            resp = cl.initRepository(repository=repository, role=role, instance=instance, force=force)
        except Exception as e:
            raise exceptions.BadRequest(str(e))
        return resp['msg']

    def install(self, repository, role='', instance='', force=False, async=False, **kwargs):
        cl = self.get_client(**kwargs)
        try:
            resp = cl.executeAction(action='install', repository=repository, async=async, force=force)
        except Exception as e:
            raise exceptions.BadRequest(str(e))
        return resp['msg']

    def simulate(self, repository, action, role='', instance='', force=False, **kwargs):
        cl = self.get_client(**kwargs)
        role = '' if not role else role
        instance = '' if not instance else instance
        resp = cl.simulateAction(repository=repository, action=action, role=role, instance=instance, force=force)
        return resp

    def executeAction(self, repository, action, role='', instance='', force=False, async=False, **kwargs):
        cl = self.get_client(**kwargs)
        role = '' if not role else role
        instance = '' if not instance else instance
        try:
            resp = cl.executeAction(repository=repository, action=action, role=role, instance=instance, force=force, async=async)
        except Exception as e:
            raise exceptions.BadRequest(str(e))
        return resp['msg']

    def deleteService(self, repository, role='', instance='', force=False, uninstall=True, **kwargs):
        cl = self.get_client(**kwargs)
        role = '' if not role else role
        instance = '' if not instance else instance
        try:
            resp = cl.deleteServiceByInstance(repository=repository, role=role, instance=instance)
        except j.exceptions.RuntimeError as e:
            raise exceptions.BadRequest(e.message)
        return "Service deleted"

    def commit(self, name, **kwargs):
        pass

    def reload(self, **kwargs):
        cl = self.get_client(**kwargs)
        try:
            cl.reloadAll()
        except j.exceptions.RuntimeError as e:
            return 'Error during reloading : %s' % e.message
        return 'Cockpit reloaded'

    def commit(self, message, branch='master', push=True, **kwargs):
        if not j.atyourservice.exist('ays_cockpit'):
            return "can't find ays repository for cockpit at /opt/code/cockpit/ays_cockpit"
        repo = j.atyourservice.get('ays_cockpit')

        sshkey_service = repo.getService('sshkey', 'main', die=False)
        if sshkey_service is None:
            return "can't find sshkey service"

        sshkey_service.actions.start(service=sshkey_service)

        if message == "" or message is None:
            message = "log changes for cockpit repo"
        gitcl = j.clients.git.get("/opt/code/cockpit")
        if branch != "master":
            gitcl.switchBranch(branch)

        gitcl.commit(message, True)

        if push:
            print("PUSH")
            gitcl.push()

        msg = "repo committed"
        if push:
            msg += ' and pushed'
        return msg
