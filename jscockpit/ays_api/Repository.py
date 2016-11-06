
from flask_wtf import Form
from wtforms.validators import DataRequired, Length, Regexp, NumberRange, required
from wtforms import TextField, FormField, IntegerField, FloatField, FileField, BooleanField, DateField, FieldList
from .input_validators import multiple_of


class Repository(Form):

    name = TextField(validators=[DataRequired(message="Name must be specified")])
    path = TextField()
    git_url = TextField(validators=[DataRequired(message="Git URL must be specified")])
