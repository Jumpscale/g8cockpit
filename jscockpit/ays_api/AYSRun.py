
from flask_wtf import Form
from wtforms.validators import DataRequired, Length, Regexp, NumberRange, required
from wtforms import TextField, FormField, IntegerField, FloatField, FileField, BooleanField, DateField, FieldList
from input_validators import multiple_of

from AYSStep import AYSStep


class AYSRun(Form):
    
    aysrepo = TextField(validators=[DataRequired(message="")])
    steps = FieldList(FormField(AYSStep))
