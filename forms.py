from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, EqualTo


class GroupForm(FlaskForm):
    name = StringField('name',
                           validators=[DataRequired()])
    location = SelectField('location', coerce=int)
    price = StringField('price')
    date = DateField('date',
                           validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Submit')

class ListForm(FlaskForm):
    date = DateField('date', format='%Y-%m-%d')
    submit = SubmitField('Submit')

class PurchaseForm(FlaskForm):
    name = StringField('name',
                           validators=[DataRequired()])
    location = SelectField('location', coerce=int)
    group = SelectField('group', coerce=int, default=1)
    price = StringField('price') 
    date = DateField('date', format='%Y-%m-%d')
    platform = SelectField('platform', coerce=int)
    not_selling = BooleanField('not_selling')
    submit = SubmitField('Submit')

class SaleForm(FlaskForm):
    name = SelectField('name', coerce=int)
    location = SelectField('location', coerce=int)
    price = StringField('price')
    date = DateField('date',
                           validators=[DataRequired()], format='%Y-%m-%d')
    tax = StringField('tax')
    paypal = SelectField('paypal', choices=[
                        ('0', 'None'),
                        ('1', 'Percent and Fee'), 
                        ('2', 'Percent Only')])
    ebay = BooleanField('ebay')
    shipping_fee = StringField('shipping_fee')
    submit = SubmitField('Submit')