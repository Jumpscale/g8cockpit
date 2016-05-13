
from flask_wtf import Form
from wtforms.validators import DataRequired, Length, Regexp, NumberRange, required
from wtforms import TextField, FormField, IntegerField, FloatField, FileField, BooleanField, DateField, FieldList
from .input_validators import multiple_of


class Service(Form):

    actions_py = TextField(validators=[DataRequired(message="")])
    instance = TextField(validators=[DataRequired(message="")])
    instance_hrd = TextField(validators=[DataRequired(message="")])
    name = TextField(validators=[DataRequired(message="")])
    state = TextField(validators=[DataRequired(message="")])
