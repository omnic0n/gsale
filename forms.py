from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo

location_list = ['garage', 'online', 'pawn', 'thrift', 'store']

class PurchaseForm(FlaskForm):
    name = StringField('name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    group = StringField('group') 
    price = StringField('price',validators=[DataRequired()]) 