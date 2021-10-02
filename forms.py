from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, EqualTo


class GroupForm(FlaskForm):
    name = StringField('name',
                           validators=[DataRequired()])
    price = StringField('price')
    date = DateField('date',
                           validators=[DataRequired()], format='%Y-%m-%d')
    id = StringField('id')
    submit = SubmitField('Submit')

class ListForm(FlaskForm):
    start = DateField('start', format='%Y-%m-%d')
    end = DateField('end', format='%Y-%m-%d')
    submit = SubmitField('Submit')

class PurchaseForm(FlaskForm):
    name = TextAreaField('name',
                           validators=[DataRequired()])
    group = SelectField('group', coerce=int, default=1)
    price = StringField('price')
    date = DateField('date', format='%Y-%m-%d')
    submit = SubmitField('Submit')

class ItemForm(FlaskForm):
    name = StringField('name',
                           validators=[DataRequired()])
    group = SelectField('group')
    sold = BooleanField('sold')
    date = DateField('date',
                           validators=[DataRequired()], format='%Y-%m-%d')
    price = StringField('price')
    shipping_fee = StringField('shipping_fee')
    id = StringField('id')
    submit = SubmitField('Submit')

class SaleForm(FlaskForm):
    name = SelectField('name', coerce=int)
    price = StringField('price')
    date = DateField('date',
                           validators=[DataRequired()], format='%Y-%m-%d')
    shipping_fee = StringField('shipping_fee')
    submit = SubmitField('Submit')