from flask import Blueprint, jsonify, request
from JumpScale import j
import os.path

project_api = Blueprint('project_api', __name__)


@project_api.route('/project', methods=['GET'])
def project_get():
    '''
    list all projects
    It is handler for GET /project
    '''
    return jsonify(projects=list(j.atyourservice.findAYSRepos()))


@project_api.route('/project', methods=['POST'])
def project_post():
    '''
    create a new project
    It is handler for POST /project
    '''
    path = request.json['path']
    j.atyourservice.createAYSRepo(path)
    return jsonify(status=0)


@project_api.route('/project', methods=['DELETE'])
def project_delete():
    '''
    delete a project
    It is handler for DELETE /project
    '''
    path = request.json['path']
    j.sal.fs.remove(os.path.join(path, '.ays'))
    return jsonify(status=0)
