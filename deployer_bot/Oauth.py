import click
from JumpScale import j
from flask import Flask
from flask import Blueprint, jsonify, request, send_from_directory
import os.path
import json
import urllib
import requests

oauth_api = Blueprint('oauth_api', __name__)

STATE_KEY = 'cockpit.deploy.state'
ORG_TOKEN_KEY = 'cockpit.deploy.orgtoken'


def get_user_token(code, state):
    params = {
        'code': code,
        'redirect_uri': app.config['redirect_uri'],
        'client_id': app.config['client_id'],
        'client_secret': app.config['client_secret'],
        'state': state,
    }
    url = '%s/v1/oauth/access_token?%s' % (app.config['itsyouonlinehost'], urllib.parse.urlencode(params))
    resp = requests.post(url, verify=False)
    resp.raise_for_status()
    # token = resp.json()['access_token']
    return resp.json()


def get_jwt():
    params = {
        'grant_type': 'client_credentials',
        'client_id': app.config['client_id'],
        'client_secret': app.config['client_secret'],
    }
    url = 'https://itsyou.online/v1/oauth/access_token?%s' % (urllib.parse.urlencode(params))
    resp = requests.post(url, verify=False)
    resp.raise_for_status()
    access_token = resp.json()['access_token']

    url = 'https://itsyou.online/v1/oauth/jwt'
    headers = {'Authorization': 'token %s' % access_token}
    data = {
        'scope': 'user:memberOf:%s' % ('personal_cockpit')
    }
    resp = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    return resp.text


def get_org_token():
    params = {
        'grant_type': 'client_credentials',
        'client_id': app.config['client_id'],
        'client_secret': app.config['client_secret']
    }
    url = '%s/v1/oauth/access_token?%s' % (app.config['itsyouonlinehost'], urllib.parse.urlencode(params))
    resp = requests.post(url, verify=False)
    resp.raise_for_status()
    token = resp.json()['access_token']
    return token


def create_api_key(organization):
    organization_token = get_org_token()

    url = '%s/api/organizations/%s/apikeys' % (app.config['itsyouonlinehost'], app.config['client_id'])
    headers = {'Authorization': 'token %s' % organization_token}
    apikey = {
        'label': organization,
    }
    resp = requests.post(url, data=json.dumps(apikey), headers=headers, verify=False)
    if resp.status_code == 409:
        # already exists
        url += '/%s' % organization
        resp = requests.get(url, headers=headers, verify=False)

    if resp.ok is False:
        j.core.db.hdel(ORG_TOKEN_KEY, organization)
        resp.raise_for_status()

    print(resp.json())
    return resp.json()['secret']


@oauth_api.route('/callback', methods=['GET'])
def callback():
    '''
    call back of oauth authorize call
    It is handler for GET /oauth
    '''
    code = request.args['code']
    state = request.args['state']
    if not j.core.db.hexists(STATE_KEY, state):
        return "state doesn't match. abort", 400

    organization = j.core.db.hget(STATE_KEY, state).decode()
    token = get_user_token(code, state)
    if token.get('scope', '') != 'user:memberof:%s' % organization:
        err_msg = "You're not part of the organization '%s'. can't deploy a Cockpit." % organization
        j.core.db.lpush(state, j.data.serializer.json.dumps({'error': err_msg}))
        return err_msg, 401

    print('token %s' % token['access_token'])
    cockpit_client_secret = create_api_key(organization)
    data = j.data.serializer.json.dumps({'client_secret': cockpit_client_secret, 'client_id': app.config['client_id']})
    j.core.db.lpush(state, data)

    return send_from_directory('templates', 'confirm.html')


@oauth_api.route('/oauthurl', methods=['GET'])
def oauthurl():
    '''
    call back of oauth authorize call
    It is handler for GET /oauth
    '''
    organization = request.args.get('organization', None)
    if not organization:
        return "bad request", 400

    state = j.data.idgenerator.generateXCharID(20)
    j.core.db.hset(STATE_KEY, state, organization)
    params = {
        'response_type': 'code',
        'client_id': app.config['client_id'],
        'redirect_uri': app.config['redirect_uri'],
        'state': state,
        'scope': 'user:memberof:%s' % organization
    }
    url = '%s/v1/oauth/authorize?%s' % (app.config['itsyouonlinehost'], urllib.parse.urlencode(params))
    return jsonify({'url': url, 'state': state})


app = Flask(__name__, static_folder='templates')


@app.route('/static/<path:path>')
def static_file(path):
    print("path: ", path)
    return send_from_directory('templates', path)

app.register_blueprint(oauth_api)

if __name__ == "__main__":
    cfg = j.data.serializer.toml.load('config.toml')
    app.config.update(cfg['oauth'])
    app.run(debug=True, host=cfg['oauth'].get('host', '0.0.0.0'), port=cfg['oauth'].get('port', 5000))
