from JumpScale import j
from flask_wtf import Form
from wtforms.validators import DataRequired, Length, Regexp, NumberRange, required, ValidationError
from wtforms import TextField, FormField, IntegerField, FloatField, FileField, BooleanField, DateField, FieldList
from .input_validators import multiple_of


class Blueprint(Form):

    content = TextField(validators=[DataRequired(message="Content can not be empty")])
    name = TextField(validators=[DataRequired(message="Name need to be specified")])
    path = TextField(validators=[])

    def validate_content(form, field):
        try:
            j.data.serializer.yaml.loads(field.data)
        except Exception as e:
            raise ValidationError("content is not valid yaml: %s" % str(e))
