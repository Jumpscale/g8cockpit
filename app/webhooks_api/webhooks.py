from flask import Blueprint, jsonify, request
# from JumpScale import j


webhooks_api = Blueprint('webhooks_api', __name__)


@webhooks_api.route('/webhooks/github', methods=['POST'])
def webhooks_github_post():
    '''
    endpoint that receives the events from github
    It is handler for POST /webhooks/github
    '''
    if 'HTTP_X_GITHUB_EVENT' not in request.headers or 'HTTP_X_GITHUB_DELIVERY' not in request.headers:
        return '', 400

    key = '%s.%s.%s' % (request.headers.get('HTTP_X_GITHUB_EVENT') , request.headers.get('HTTP_X_GITHUB_DELIVERY'), j.data.time.epoch)
    j.core.db.hset('webhooks', key, request.data)
    return '', 201
