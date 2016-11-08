from flask_wtf import Form
from wtforms.validators import DataRequired
from wtforms import TextField, FormField


class Actor(Form):
    actions_py = TextField(validators=[DataRequired(message="")])
    name = TextField(validators=[DataRequired(message="")])
    schema_hrd = TextField(validators=[DataRequired(message="")])
