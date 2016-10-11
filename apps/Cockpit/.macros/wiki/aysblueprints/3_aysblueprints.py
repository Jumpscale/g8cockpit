


def main(j, args, params, tags, tasklet):
    ayspath = args.getTag('ayspath')

    try:
        bps = {}
        for ayspath, blueprints in j.apps.cockpit.atyourservice.listBlueprints(ayspath, ctx=args.requestContext).items():

            if ayspath not in bps:
                bps[ayspath] = []

            for blueprint in blueprints:
                bp = {}
                bp['title'] = j.sal.fs.getBaseName(blueprint['path'])
                bp['label_content'] = 'archived' if blueprint['archived'] else 'enable'
                bp['icon'] = 'saved' if blueprint['archived'] else 'ok'
                bp['label_color'] = 'warning' if blueprint['archived'] else 'success'
                bp['content'] = j.data.serializer.json.dumps(blueprint['content'])
                bps[ayspath].append(bp)

        args.doc.applyTemplate({'data': bps})
    except Exception as e:
        args.doc.applyTemplate({'error': str(e)})

#     result.append("""
# {{html:
# <script src='/jslib/codemirror/autorefresh.js'></script>
# }}
# {{jscript
#   $(function() {
#       $('.label').click(function() {
#         var that = this
#         var ss = this.id.split('-')
#         var repo = ss.shift()
#         var bp = ss.join('-')
#         if (this.innerText == 'enable'){
#             var url = '/restmachine/cockpit/atyourservice/archiveBlueprint';
#         }else{
#             var url = '/restmachine/cockpit/atyourservice/restoreBlueprint';
#         }
#         $.ajax({
#           type: 'GET',
#           data: 'repository='+repo+'&blueprint='+bp,
#           success: function(result,status,xhr) {
#             // restore
#             if (that.innerText == 'archived'){
#                 that.classList.remove('glyphicon-saved');
#                 that.classList.remove('label-warning');
#                 that.classList.add('glyphicon-ok');
#                 that.classList.add('label-sucess');
#                 that.innerText = 'enable'
#             }else{ // archive
#                 that.classList.remove('glyphicon-ok');
#                 that.classList.remove('label-sucess');
#                 that.classList.add('label-warning');
#                 that.classList.add('glyphicon-saved');
#                 that.innerText = 'archived'
#             }
#           },
#           error: function(xhr,status,error){ alert('error:'+ error) },
#           url: url,
#           cache:false
#         });
#       });
#     });
# }}
# {{cssstyle
# a.label-archive{
#     color: white;
# }
# }}""")
    # result = '\n'.join(result)

    params.result = (args.doc, args.doc)
    return params
