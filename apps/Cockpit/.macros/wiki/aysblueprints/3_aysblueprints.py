
def main(j, args, params, tags, tasklet):
    ayspath = args.getTag('ayspath')
    result = list()
    result.append('''{{html: <div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">}}''')

    for ayspath, blueprints in j.apps.system.atyourservice.listBlueprints(ayspath, ctx=args.requestContext).items():
        result.append('{{html: <h4> %s </h4>}}' % ayspath)
        for blueprint in blueprints:
            bpid = blueprint['path'].replace('/', '')
            bpid = bpid.rsplit('.' + j.sal.fs.getFileExtension(bpid))[0]
            sectionid = 'collapse_%s' % bpid
            headingid = 'heading_%s' % bpid
            archived = 'archived' if blueprint['archived'] else 'enable'
            icon = 'saved' if blueprint['archived'] else 'ok'
            label = 'warning' if blueprint['archived'] else 'success'
            label_id = "%s-%s" % (ayspath, blueprint['name'])
            result.append("""{{html:
<div class="panel panel-default">
  <div class="panel-heading" role="tab" id="%(headingid)s">
    <h4 class="panel-title">
      <a data-toggle="collapse" data-parent="#accordion" href="#%(sectionid)s" aria-expanded="true" aria-controls="%(sectionid)s"> %(name)s</a>
        <a id=%(labelid)s class="label-archive label label-%(label)s glyphicon glyphicon glyphicon-%(icon)s pull-right">%(archived)s</a>
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
}}""" % {'headingid': headingid, 'sectionid': sectionid, 'name': blueprint['name'],
                'content': blueprint['content'],
                'archived': archived, 'icon': icon, 'label': label, 'labelid': label_id})

    result.append("""
{{html:
<script src='/jslib/codemirror/autorefresh.js'></script>
}}
{{jscript
  $(function() {
      $('.label').click(function() {
        that = this
        id = this.id
        ss = id.split('-')
        repo = ss[0]
        bp = ss[1]
        if (this.innerText == 'enable'){
            url = '/restmachine/system/atyourservice/archiveBlueprint';
        }else{
            url = '/restmachine/system/atyourservice/restoreBlueprint';
        }
        $.ajax({
          type: 'GET',
          data: 'repository='+repo+'&blueprint='+bp,
          success: function(result,status,xhr) {
            // restore
            if (that.innerText == 'archived'){
                that.classList.remove('glyphicon-saved');
                that.classList.remove('label-warning');
                that.classList.add('glyphicon-ok');
                that.classList.add('label-sucess');
                that.innerText = 'enable'
            }else{ // archive
                that.classList.remove('glyphicon-ok');
                that.classList.remove('label-sucess');
                that.classList.add('label-warning');
                that.classList.add('glyphicon-saved');
                that.innerText = 'archived'
            }
          },
          error: function(xhr,status,error){ alert('error:'+ error) },
          url: url,
          cache:false
        });
      });
    });
}}
{{cssstyle
a.label-archive{
    color: white;
}
}}""")
    result = '\n'.join(result)

    params.result = (result, args.doc)
    return params
