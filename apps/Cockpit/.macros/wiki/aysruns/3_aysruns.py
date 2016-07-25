from collections import OrderedDict

def main(j, args, params, tags, tasklet):
    import jinja2
    params.result = page = args.page
    doc = args.doc
    arg_repo = args.getTag('repo')
    klass = 'jstimestamp'


    out = list()
    # this makes sure bootstrap datatables functionality is used
    out.append("{{datatables_use}}\n{{timestamp}}\n")
    for repo_path, runs in j.apps.cockpit.atyourservice.listRuns(repository=arg_repo, ctx=args.requestContext).items():
        out.append('h5. AYSRepo: %s' % repo_path)
        html = '''
<table class="table table-striped table-bordered display JSdataTable dataTable">
<thead>
  <td>Run ID</td><td>Run AT</td><td>State</td>
</thead>
{% for run in runs %}
<tr>
  <td><a data-dummy="{{run.sortkey}}" href="cockpit/Run?repo={{repo_path}}&runid={{run.id}}">{{run.id}}</a></td>
  <td><span class="jstimestamp" data-ts="{{run.runat}}"></span></td>
  <td>{{run.state}}</td>
</tr>
{% endfor %}
</table>
        '''
        template = jinja2.Template(html)
        aysruns = []
        for key, value in runs['aysruns'].items():
            runat, state = value.split('|')
            runid = int(key)
            aysrun = {'id': runid,
                      'state': state,
                      'sortkey': '%05d' % runid,
                      'runat': runat}
            aysruns.append(aysrun)

        table = "{{html:\n%s\n}}" % template.render(runs=sorted(aysruns, key=lambda x: x['id']), repo_path=repo_path)
        out.append(table)

    out = '\n'.join(out)
    params.result = (out, doc)

    return params
