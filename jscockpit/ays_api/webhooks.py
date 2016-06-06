from flask import Blueprint, jsonify, request
from JumpScale import j


webhooks_api = Blueprint('webhooks_api', __name__)


@webhooks_api.route('/webhooks/github', methods=['POST'])
def webhooks_github_post():
    '''
    endpoint that receives the events from github
    It is handler for POST /webhooks/github
    '''
    if 'X-GitHub-Event' not in request.headers or 'X-GitHub-Delivery' not in request.headers:
        return '', 400

    key = '%s.%s.%s' % (request.headers.get('X-GitHub-Event'), request.headers.get('X-GitHub-Delivery'), j.data.time.epoch)
    j.core.db.hset('webhooks', key, j.data.serializer.json.dumps(request.json))

    # send event to notify reception of webhooks
    event = j.data.models.cockpit_event.Generic()
    event.args = {
        'source': 'github',
        'event': request.headers.get('X-GitHub-Event'),
        'key': key,
    }
    j.core.db.publish('generic', event.to_json())

    return '', 201
