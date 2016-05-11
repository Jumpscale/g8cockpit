from flask import Blueprint, jsonify, request



oauth_api = Blueprint('oauth_api', __name__)


@oauth_api.route('/oauth/callback', methods=['GET'])
def oauth_callback_get():
    '''
    Callback endpoint for oauth
    It is handler for GET /oauth/callback
    '''
    
    return jsonify()
