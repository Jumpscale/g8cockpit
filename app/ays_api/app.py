from flask import Flask, send_from_directory
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



@app.route('/apidocs/<path:path>')
def send_js(path):
    root = j.sal.fs.joinPaths(__file__, 'apidocs')
    return send_from_directory(root, path)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
