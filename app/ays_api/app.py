from flask import Flask

from .blueprint import blueprint_api
from .project import project_api
from .service import service_api
from .template import template_api
from .oauth import oauth_api


app = Flask(__name__)

app.register_blueprint(blueprint_api)
app.register_blueprint(project_api)
app.register_blueprint(service_api)
app.register_blueprint(template_api)
app.register_blueprint(oauth_api)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
