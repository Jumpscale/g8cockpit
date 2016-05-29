from flask import Flask, send_from_directory, make_response, request
import jwt
import wtforms_json
from .ays import ays_api
from .oauth import oauth_api
from .webhooks import webhooks_api


app = Flask(__name__)

app.config["WTF_CSRF_ENABLED"] = False
wtforms_json.init()


def process_jwt_token():
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
    msg = ""
    if type.lower() == 'bearer':
        try:
            headers = jwt.get_unverified_header(token)
            payload = jwt.decode(token, app.config.get('jwt_key'), algorithm=headers['alg'], audience=app.config['organization'], issuer='itsyouonline')
            # case JWT is for an organization
            if 'globalid' in payload and payload['globalid'] == app.config.get('organization'):
                return

            # case JWT is for a user
            if 'scope' in payload and 'user:memberOf:%s' % app.config.get('organization') in payload['scope'].split(','):
                return

            msg = 'Unauthorized'
        except jwt.ExpiredSignatureError as e:
            msg = 'Your JWT has expired'

        except jwt.DecodeError as e:
            msg = 'Your JWT is invalid'

    else:
        msg = 'Your JWT is invalid'

    response = make_response(msg)
    response.status_code = 401
    return response


ays_api.before_request(process_jwt_token)
app.register_blueprint(ays_api)
app.register_blueprint(oauth_api)
app.register_blueprint(webhooks_api)


@app.route('/apidocs/<path:path>')
def send_js(path):
    root = j.sal.fs.joinPaths(__file__, 'apidocs')
    return send_from_directory(root, path)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
