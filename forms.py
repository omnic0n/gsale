from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, EqualTo


class PurchaseForm(FlaskForm):
    name = StringField('name',
                           validators=[DataRequired()])
    location = SelectField('location', coerce=int)
    price = StringField('price') 
    date = DateField('date',
                           validators=[DataRequired()], format='%Y-%m-%d')
    platform = SelectField('platform', coerce=int)
    submit = SubmitField('Submit')