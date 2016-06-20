
from flask_wtf import Form
from wtforms.validators import DataRequired, Length, Regexp, NumberRange, required
from wtforms import TextField, FormField, IntegerField, FloatField, FileField, BooleanField, DateField, FieldList
from input_validators import multiple_of



class AYSStep(Form):
    
    action = TextField(validators=[DataRequired(message="")])
    number = IntegerField(validators=[DataRequired(message="")])
    services_keys = FieldList(TextField('services_keys', [required()]), DataRequired(message=""))
