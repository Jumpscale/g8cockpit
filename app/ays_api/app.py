from flask import Flask, send_from_directory, make_response, request
import jwt
import wtforms_json
from .ays import ays_api
from .oauth import oauth_api
from .webhooks import webhooks_api


app = Flask(__name__)

app.config["WTF_CSRF_ENABLED"] = False
wtforms_json.init()

app.register_blueprint(ays_api)
app.register_blueprint(oauth_api)
app.register_blueprint(webhooks_api)

@app.before_request
def process_token():
    authorization = request.cookies.get(
        'jwt',
        request.headers.get(
            'Authorization',
            None
        ))

    if authorization is None:
        response = make_response('Not JWT token')
        response.status_code = 401
        return response

    type, token = authorization.split(' ', 1)
    if type.lower() == 'bearer':
        try:
            headers = jwt.get_unverified_header(token)
            payload = jwt.decode(token, app.config.get('jwt_key'), algorithm=headers['alg'], audience=app.config['organization'], issuer='itsyouonline')
            if 'scope' not in payload or \
               'user:memberOf:%s' % app.config.get('organization') not in payload['scope'].split(','):
                response = make_response('Unauthorized')
                response.status_code = 401
                return response

        except jwt.ExpiredSignatureError as e:
            response = make_response('Your JWT has expired')
            response.status_code = 401
            return response
        except jwt.DecodeError as e:
            response = make_response('Your JWT is invalid')
            response.status_code = 401
            return response
    else:
        response = make_response('Your JWT is invalid')
        response.status_code = 401
        return response



@app.route('/apidocs/<path:path>')
def send_js(path):
    root = j.sal.fs.joinPaths(__file__, 'apidocs')
    return send_from_directory(root, path)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
