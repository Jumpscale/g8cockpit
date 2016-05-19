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
    token = request.cookies.get(
        'jwt',
        request.headers.get(
            'Authorization',
            jwt.encode({'exp': 0}, app.config.get('jwt_key'))
        ))
    try:
        payload = jwt.decode(token, app.config.get('jwt_key'))
        if 'scope' not in payload or \
           payload['scope'].find('user:memberOf:%s' % app.config.get('organization')) == -1:
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


@app.route('/apidocs/<path:path>')
def send_js(path):
    root = j.sal.fs.joinPaths(__file__, 'apidocs')
    return send_from_directory(root, path)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
