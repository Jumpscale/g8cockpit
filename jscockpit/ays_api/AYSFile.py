
from flask_wtf import Form
from wtforms.validators import DataRequired
from wtforms import TextField


class AYSFile(Form):
    content = TextField(validators=[DataRequired(message="")])
