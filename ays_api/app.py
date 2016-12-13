from flask import Flask, send_from_directory, make_response, request, send_file, jsonify
import werkzeug.exceptions
from jose import jwt, exceptions
import wtforms_json
from .ays import ays_api
from .oauth import oauth_api
from .webhooks import webhooks_api
from .cockpit import cockpit_api
from JumpScale import j


app = Flask(__name__)

app.config["WTF_CSRF_ENABLED"] = False
wtforms_json.init()

logger = j.logger.get('j.cockpit.api')

def init_blueprints():
    if app.config.get('production',True):
        print('JWT middleware enable')
        ays_api.before_request(process_jwt_token)
        cockpit_api.before_request(process_jwt_token)

    app.register_blueprint(ays_api)
    app.register_blueprint(oauth_api)
    app.register_blueprint(webhooks_api)
    app.register_blueprint(cockpit_api)



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

    msg = ""
    ss = authorization.split(' ', 1)
    if len(ss) != 2:
        msg = "Unauthorized"
    else:
        type, token = ss[0], ss[1]
        if type.lower() == 'bearer':
            try:
                headers = jwt.get_unverified_header(token)
                payload = jwt.decode(
                    token,
                    app.config['oauth'].get('jwt_key'),
                    algorithms=[headers['alg']],
                    audience=app.config['oauth']['organization'],
                    issuer='itsyouonline')
                # case JWT is for an organization
                if 'globalid' in payload and payload['globalid'] == app.config['oauth'].get('organization'):
                    return

                # case JWT is for a user
                if 'scope' in payload and 'user:memberof:%s' % app.config[
                        'oauth'].get('organization') in payload['scope']:
                    return

                msg = 'Unauthorized'
            except exceptions.ExpiredSignatureError as e:
                msg = 'Your JWT has expired'

            except exceptions.JOSEError as e:
                msg = 'JWT Error: %s' % str(e)

            except Exception as e:
                msg = 'Unexpected error : %s' % str(e)

        else:
            msg = 'Your JWT is invalid'

    logger.error(msg)
    response = make_response(msg)
    response.status_code = 401
    return response

@app.route('/apidocs/<path:path>')
def send_js(path):
    root = j.sal.fs.joinPaths(j.sal.fs.getParent(__file__), 'apidocs')
    return send_from_directory(root, path)


@app.route('/', methods=['GET'])
def home():
    path = j.sal.fs.joinPaths(j.sal.fs.getParent(__file__), 'index.html')
    return send_file(path)


@app.errorhandler(j.exceptions.NotFound)
def handle_bad_request(e):
    return jsonify(error=e.msg), 404


@app.errorhandler(j.exceptions.AYSNotFound)
def handle_bad_request(e):
    return jsonify(error=e.msg), 404


@app.errorhandler(j.exceptions.Timeout)
def handle_bad_request(e):
    return jsonify(error=e.msg), 408


@app.errorhandler(j.exceptions.BaseJSException)
def handle_bad_request(e):
    return jsonify(error=e.msg), 500


@app.errorhandler(werkzeug.exceptions.HTTPException)
def handle_bad_request(e):
    return jsonify(error=e.msg), e.code