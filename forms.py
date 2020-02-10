from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo


class PurchaseForm(FlaskForm):
    location_list = [('garage', 'garage'), 
                     ('online', 'online'),
                     ('pawn', 'pawn'),
                     ('thrift', 'thrift'),
                     ('store','store')]
    name = StringField('name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    location = SelectField('location', choices=location_list)
    group = SelectField('group') 
    price = StringField('price',validators=[DataRequired()]) 
    submit = SubmitField('Submit')