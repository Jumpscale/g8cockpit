from JumpScale import j

class cockpit_manager(j.tools.code.classGetBase()):
    """
    cockpit actor
    """

    def update(self, **kwargs):
        """
        Update cockpit
        result json
        """
        if '/opt/code/cockpit/ays_cockpit' not in j.atyourservice.repos:
            return
        repo = j.atyourservice.repos['/opt/code/cockpit/ays_cockpit']
        restuls = repo.findServices(templatename='os.cockpit')
        if len(restuls) > 1:
            raise j.exceptions.RuntimeError("too many service os.cockpit found")
        elif len(restuls) <= 0:
            raise j.exceptions.AYSNotFound("service os.cockpit not found")
        elif len(restuls) == 1:
            service = restuls[0]
            service.actions.update(service=service)
