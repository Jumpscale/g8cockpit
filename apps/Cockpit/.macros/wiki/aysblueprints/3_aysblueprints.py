
def main(j, args, params, tags, tasklet):
    ayspath = args.getTag('ayspath')
    result = list()
    result.append('''{{html: <div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">}}''')

    for ayspath, blueprints in j.apps.system.atyourservice.listBlueprints(ayspath).items():
        result.append('{{html: <h4> %s </h4>}}' % ayspath)

        for blueprint in blueprints:
          bpid = blueprint.path.replace('/', '')
          bpid = bpid.rsplit('.yaml')[0]
          sectionid = 'collapse_%s' % bpid
          headingid = 'heading_%s' % bpid
          result.append("""{{html:
<div class="panel panel-default">
  <div class="panel-heading" role="tab" id="%(headingid)s">
    <h4 class="panel-title">
      <a data-toggle="collapse" data-parent="#accordion" href="#%(sectionid)s" aria-expanded="true" aria-controls="%(sectionid)s"> %(path)s</a>
    </h4>
    </div>
    <div id="%(sectionid)s" class="panel-collapse collapse" role="tabpanel" aria-labelledby="%(headingid)s">
      <div class="panel-body">
}}
{{code autorefresh:
%(content)s
}}
{{html:

      </div>
  </div>
</div>
}}""" % {'headingid': headingid, 'sectionid': sectionid, 'path': j.sal.fs.getBaseName(blueprint.path),
         'content': blueprint.content})

    result.append("""{{html:
  <script src='/jslib/codemirror/autorefresh.js'></script>
        </div>
        }}""")
    result = '\n'.join(result)

    params.result = (result, args.doc)
    return params
