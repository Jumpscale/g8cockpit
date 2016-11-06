
from flask_wtf import Form
from wtforms.validators import DataRequired, ValidationError
from wtforms import TextField


class ActorRepo(Form):

    branch = TextField(validators=[DataRequired(message="branch can't be empty'")])
    url = TextField(validators=[DataRequired(message="url can't be empty")])

    def validate_url(form, field):
        if not field.data.startswith('http'):
            raise ValidationError("URL Format not valid. It should starts with http")


