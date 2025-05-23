from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, BooleanField, FileField, HiddenField, FormField, FieldList, TextField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, EqualTo
from datetime import datetime

class GroupForm(FlaskForm):
    name = StringField('name',
                           validators=[DataRequired()])
    price = StringField('price')
    date = DateField('date',
                        default=datetime.today,
                        validators=[DataRequired()], format='%Y-%m-%d')
    id = StringField('id')
    image = FileField('image')

    listYear = SelectField('Year', default=datetime.now().year, choices=[
        (2021), (2022), (2023), (2024), (2025), ("All")
    ])
    submit = SubmitField('Submit')

class ExpenseForm(FlaskForm):
    name = StringField('name',
                           validators=[DataRequired()])
    price = StringField('price')
    date = DateField('date',
                        default=datetime.today,
                        validators=[DataRequired()], format='%Y-%m-%d')
    id = StringField('id')
    expense_type = SelectField('expense_type', coerce=int)
    milage = StringField('milage')
    image = FileField('image')
    submit = SubmitField('Submit')

class ListForm(FlaskForm):
    start = DateField('start', format='%Y-%m-%d')
    end = DateField('end', format='%Y-%m-%d')
    submit = SubmitField('Submit')


class PurchaseForm(FlaskForm):
    itemList = FieldList(TextField(validators=[DataRequired()]), min_entries=0)
    group = SelectField('group', coerce=str)
    category = SelectField('category', coerce=int)
    price = StringField('price')
    list_date = DateField('List Date',
                        default=datetime.today,
                        validators=[DataRequired()], format='%Y-%m-%d')
    storage = StringField('storage')
    submit = SubmitField('Submit')

class ItemForm(FlaskForm):
    name = StringField('name',
                           validators=[DataRequired()])
    group = SelectField('group', coerce=str)
    sale_date = DateField('Sale Date',
                        default=datetime.today,
                        validators=[DataRequired()], format='%Y-%m-%d')
    list_date = DateField('List Date',
                        default=datetime.today,
                        validators=[DataRequired()], format='%Y-%m-%d')
    price = StringField('price')
    shipping_fee = StringField('shipping_fee')
    id = StringField('id')
    storage = StringField('storage')
    category = SelectField('category', coerce=int)
    returned = SelectField('returned', coerce=int)
    sold = SelectField('sold', choices=[
        (0, 'No'),(1, 'Yes'), ('%', 'All')])
    submit = SubmitField('Submit')

class SaleForm(FlaskForm):
    id = SelectField('id', coerce=str)
    price = StringField('price')
    sale_date = DateField('date',
                        default=datetime.today,
                        validators=[DataRequired()], format='%Y-%m-%d')
    shipping_fee = StringField('shipping_fee')
    submit = SubmitField('Submit')

class ReportsForm(FlaskForm):
    type = SelectField('Type', 
                        choices=[(0, "Date"), (1, "Month"), (2, "Year"), (3, "Day")])
    date = DateField('date',
                        default=datetime.today,
                        validators=[DataRequired()], format='%Y-%m-%d')
    month = SelectField('Month', default=datetime.now().month, choices=[
        (1,"January"),(2, "February"),(3, "March"),(4, "April"),(5, "May"),(6, "June"),(7, "July"),(8, "August"),(9, "September"),(10, "October"),(11, "November"),(12, "December")
    ])
    year = SelectField('Year', default=datetime.now().year, choices=[
        (2021), (2022), (2023), (2024), (2025), ("All")
    ])
    day = SelectField('Day', choices=[
        (1,"Sunday"),(2, "Monday"),(3, "Tuesday"),(4, "Wednesday"),(5, "Thursday"),(6, "Friday"),(7, "Saturday")
    ])
    expense_type = SelectField('type', coerce=int)
    category = SelectField('category', coerce=int)
    submit = SubmitField('Submit')


class CasesForm(FlaskForm):
    name = StringField('name',
                        validators=[DataRequired()])
    itemList = FieldList(TextField(validators=[DataRequired()]), min_entries=0)
    platform = SelectField('platform', coerce=int)
    id = StringField('id')
    submit = SubmitField('Submit')

class ButtonForm(FlaskForm):
    button = SubmitField()
    id = HiddenField()
    info = HiddenField()

