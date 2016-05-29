from flask import Blueprint, current_app, jsonify, request
import requests
import urllib
from JumpScale import j

oauth_api = Blueprint('oauth_api', __name__)
STATE_KEY = 'cockpit.telegram.state'


def get_user_token(code, state):
    params = {
        'code': code,
        'redirect_uri': current_app.config['oauth']['redirect_uri'],
        'client_id': current_app.config['oauth']['client_id'],
        'client_secret': current_app.config['oauth']['client_secret'],
        'state': state,
    }
    url = '%s/v1/oauth/access_token?%s' % (current_app.config['oauth']['itsyouonlinehost'], urllib.parse.urlencode(params))
    resp = requests.post(url, verify=False)
    resp.raise_for_status()
    return resp.json()


@oauth_api.route('/oauth/callback', methods=['GET'])
def oauth_callback_get():
    '''
    Callback endpoint for oauth
    It is handler for GET /oauth/callback
    '''
    code = request.args['code']
    state = request.args['state']
    ss = state.split('.')
    if len(ss) != 2:
        return "wrong state. abort", 400

    user_id, random = ss[0], ss[1]
    data = j.core.db.hget(STATE_KEY, user_id)
    if data is None:
        return "state doesn't match. abort", 400
    data = j.data.serializer.json.loads(data.decode())

    if data['random'] != random:
        return "state doesn't match. abort", 400

    organization = data['organization']
    token = get_user_token(code, state)
    if token.get('scope', '') != 'user:memberof:%s' % organization:
        err_msg = "You're not part of the organization '%s'." % organization
        j.core.db.lpush(state, j.data.serializer.json.dumps({'error': err_msg}))
        return err_msg, 401

    data = j.data.serializer.json.dumps(token)
    j.core.db.lpush(state, data)

    return "Authorize"
