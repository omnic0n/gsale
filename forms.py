from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo


class PurchaseForm(FlaskForm):
    name = StringField('name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    location = SelectField('location', coerce=int)
    group = SelectField('group', coerce=int) 
    price = StringField('price') 
    date = StringField('date',
                           validators=[DataRequired(), Length(min=8, max=8)])
    description = StringField('description')
    submit = SubmitField('Submit')

class AddGroup(FlaskForm):
    name = StringField('name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    location = SelectField('location', coerce=int)
    date = StringField('date',
                           validators=[DataRequired(), Length(min=8, max=8)])
    submit = SubmitField('Submit')