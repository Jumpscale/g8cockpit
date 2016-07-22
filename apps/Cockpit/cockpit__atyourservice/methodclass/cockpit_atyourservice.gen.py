from JumpScale import j

class cockpit_atyourservice(j.tools.code.classGetBase()):
    """
    gateway to atyourservice
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="atyourservice"
        self.appname="cockpit"
        #cockpit_atyourservice_osis.__init__(self)


    def addTemplateRepo(self, url, branch, **kwargs):
        """
        Add a new service template repository.
        param:url Service template repository URL
        param:branch Branch of the repo to use default:master
        result str
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addTemplateRepo")

    def archiveBlueprint(self, repository, blueprint, **kwargs):
        """
        archive a blueprint
        param:repository repository name
        param:blueprint blueprint name
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method archiveBlueprint")

    def cockpitUpdate(self, **kwargs):
        """
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method cockpitUpdate")

    def commit(self, branch, push, message, **kwargs):
        """
        Commit change in the cockpit repo.
        param:branch branch to commit on
        param:push push after commit
        param:message name of the repository
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method commit")

    def createRepo(self, name, **kwargs):
        """
        Create AYS repository
        param:name name of the repository
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method createRepo")

    def deleteRepo(self, repository, **kwargs):
        """
        Delete AYS repository
        param:repository name of the repository
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteRepo")

    def deleteService(self, repository, role, instance, **kwargs):
        """
        Uninstall a service
        param:repository name of the repository
        param:role role of the services to delete
        param:instance instance name of the service to delete
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method deleteService")

    def executeAction(self, repository, action, role, instance, force, async, **kwargs):
        """
        Run execute on AYS repository
        param:repository name of the repository
        param:action name of the action to execute
        param:role role of the services to simulate action on
        param:instance instance name of the service to simulate action on
        param:force force the action or not
        param:async execution action asynchronously
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method executeAction")

    def executeBlueprint(self, repository, blueprint, role, **kwargs):
        """
        execute all blueprints
        param:repository blueprints in that base path will only be returned otherwise all paths
        param:blueprint blueprint name
        param:role role
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method executeBlueprint")

    def getService(self, repository, role, instance, **kwargs):
        """
        get one services
        param:repository services in that base path will only be returned otherwise all paths
        param:role service role
        param:instance service instance
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getService")

    def getTemplate(self, repository, template, **kwargs):
        """
        list ays templates
        param:repository repository in which look for template
        param:template template name
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getTemplate")

    def init(self, repository, role, instance, force, **kwargs):
        """
        Run init on AYS repository
        param:repository name of the repository
        param:role role of the services to simulate action on
        param:instance instance name of the service to simulate action on
        param:force force init
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method init")

    def install(self, repository, role, instance, force, async, **kwargs):
        """
        Run install on AYS repository
        param:repository name of the repository
        param:role role of the services to simulate action on
        param:instance instance name of the service to simulate action on
        param:force force install
        param:async execution action asynchronously
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method install")

    def listBlueprints(self, repository, archived, **kwargs):
        """
        list all blueprints
        param:repository blueprints in that base path will only be returned otherwise all paths
        param:archived include archived blueprints or not
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listBlueprints")

    def listRepos(self, **kwargs):
        """
        list all repository
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listRepos")

    def listServices(self, repository, templatename, role, **kwargs):
        """
        list all services
        param:repository services in that base path will only be returned otherwise all paths
        param:templatename only services with this templatename else all service names
        param:role only services with this role else all service names
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listServices")

    def listTemplates(self, repository, **kwargs):
        """
        list ays templates
        param:repository services in that base path will only be returned otherwise all paths
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listTemplates")

    def reload(self, **kwargs):
        """
        Unload all services from memory and force reload.
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method reload")

    def restoreBlueprint(self, repository, blueprint, **kwargs):
        """
        restore a blueprint
        param:repository repository name
        param:blueprint blueprint name
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method restoreBlueprint")

    def simulate(self, repository, action, role, instance, **kwargs):
        """
        Run simulate on AYS repository
        param:repository name of the repository
        param:action action name to simulate
        param:role role of the services to simulate action on
        param:instance instance name of the service to simulate action on
        result json
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method simulate")
