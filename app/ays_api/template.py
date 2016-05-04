from flask import Blueprint, jsonify, request
from JumpScale import j
import os

template_api = Blueprint('template_api', __name__)

def get_template_dict(template):
    return {
        'domain':template.domain,
        'key':template.key,
        'model':template.model,
        'name':template.name,
        'path':template.path,
        'path_actions':template.path_actions,
        'path_actions_node':template.path_actions_node,
        'path_hrd_schema':template.path_hrd_schema,
        'path_hrd_template':template.path_hrd_template,
        'path_mongo_model':template.path_mongo_model,
        'role':template.role,
        'schema':template.schema.content,
        'version':template.version
    }


@template_api.route('/template', methods=['GET'])
def template_get():
    '''
    list all templates
    It is handler for GET /template
    '''
    path = request.args.get('path')
    j.atyourservice.basepath = path
    return jsonify(templates=list(map(get_template_dict, j.atyourservice.templates)))


@template_api.route('/template', methods=['POST'])
def template_post():
    '''
    create new template
    It is handler for POST /template
    '''
    path = request.args.get('path')
    j.atyourservice.basepath = path
    dest = os.path.join(path,'servicetemplates',request.json['name'])
    j.sal.fs.createDir(dest)
    j.sal.fs.writeFile(os.path.join(dest, 'schema.hrd'),'')
    j.sal.fs.writeFile(os.path.join(dest, 'actions.py'),"""
        class Actions():
            def __init__():
                raise NotImplementedError()
    """)
    return jsonify(status=0)


@template_api.route('/template/<name>', methods=['GET'])
def template_byName_get(name):
    '''
    get a template
    It is handler for GET /template/<name>
    '''
    path = request.args.get('path')
    j.atyourservice.basepath = path
    return jsonify(template=get_template_dict(j.atyourservice.getTemplate(name)))
