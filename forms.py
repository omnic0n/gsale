from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
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

class SaleForm(FlaskForm):
    name = SelectField('name', coerce=int)
    location = SelectField('location', coerce=int)
    price = StringField('price')
    date = DateField('date',
                           validators=[DataRequired()], format='%Y-%m-%d')
    tax = BooleanField('taxable')
    paypal = BooleanField('paypal_used')
    ebay = BooleanField('ebay_used')
    shipping_fee = SelectField('shipping_fee', coerce=int)
    submit = SubmitField('Submit')