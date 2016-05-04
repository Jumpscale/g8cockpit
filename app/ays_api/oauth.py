from flask import Flask
from flask import Blueprint, jsonify, request
from JumpScale import j
import os.path
import urllib
import requests

oauth_api = Blueprint('oauth_api', __name__)

client_id = 'G8cockpit'
client_secret = 'NiEuDHUcIr5pvpdmjW38j6q_tZd7j4tzCx0eKBSEovWs6quTG6n0'
redirect_uri = 'https://79b0d446.ngrok.io/callback'
states_db = {}
organization_token = None


def get_user_token(code, state):
    params = {
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
        'state': state,
    }
    url = 'https://itsyou.online/v1/oauth/access_token?%s' % urllib.parse.urlencode(params)
    resp = requests.post(url)
    resp.raise_for_status()
    # handle error
    print(resp.json())
    token = resp.json()['access_token']
    return token


def get_org_token():
    params = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    url = 'https://itsyou.online/v1/oauth/access_token?%s' % urllib.parse.urlencode(params)
    resp = requests.post(url)
    # handle error
    print(resp.json())
    token = resp.json()['access_token']
    return token

def create_api_secret():
    if organization_token is None:
        organization_token = get_org_token()



@oauth_api.route('/callback', methods=['GET'])
def callback():
    '''
    call back of oauth authorize call
    It is handler for GET /oauth
    '''
    code = request.args['code']
    state = request.args['state']
    if state not in states_db:
        return "state doesn't match. abort"
    username = states_db.pop(state)
    print('get token')
    token = get_user_token(code, state)
    print('token %s' % token)
    return "recevied token %s " % token


@oauth_api.route('/login', methods=['GET'])
def login():
    '''
    call back of oauth authorize call
    It is handler for GET /oauth
    '''
    state = j.data.idgenerator.generateXCharID(10)
    states_db[state] = 'username'
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': state,  # TODO generate random, see if can be used as key to link request with user
        'scope': 'user:memberof:OrgTest'
    }
    url = 'https://itsyou.online/v1/oauth/authorize?%s' % urllib.parse.urlencode(params)
    return """<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title></title>
    </head>
    <body>
        <a href="%s">login</a>
    </body>
</html>""" % url



if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(oauth_api)
    app.run(debug=True, host='0.0.0.0', port=8080)
