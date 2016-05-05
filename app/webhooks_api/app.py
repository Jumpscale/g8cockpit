from flask import Flask, send_from_directory
import wtforms_json
from .webhooks import webhooks_api
from JumpScale import j


app = Flask(__name__)

app.config["WTF_CSRF_ENABLED"] = False
wtforms_json.init()

app.register_blueprint(webhooks_api)


@app.route('/apidocs/<path:path>')
def send_js(path):
    parent = j.sal.fs.getParent(__file__)
    dir_path = j.sal.fs.joinPaths(parent, 'apidocs')
    return send_from_directory(dir_path, path)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
