from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, BooleanField, FileField, HiddenField, FormField, FieldList, DateField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange
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
    
    # Location fields
    latitude = HiddenField('latitude')
    longitude = HiddenField('longitude')
    location_address = StringField('location_address')

    listYear = SelectField('Year', default=datetime.now().year, choices=[
        (2021), (2022), (2023), (2024), (2025), ("All")
    ])
    submit = SubmitField('Submit')



class ListForm(FlaskForm):
    start = DateField('start', format='%Y-%m-%d')
    end = DateField('end', format='%Y-%m-%d')
    submit = SubmitField('Submit')


class ItemDetailForm(FlaskForm):
    """Form for individual item details"""
    name = StringField('Item Name', validators=[DataRequired(), Length(max=150)])
    category = SelectField('Category', coerce=str, validators=[DataRequired()])
    ebay_item_id = StringField('eBay Item ID', validators=[Length(max=50)])

class PurchaseForm(FlaskForm):
    items = FieldList(FormField(ItemDetailForm), min_entries=1, max_entries=50)
    group = SelectField('group', coerce=str)
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
    category = SelectField('category', coerce=str)
    ebay_item_id = StringField('eBay Item ID', validators=[Length(max=50)])
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

    category = SelectField('category', coerce=str)
    submit = SubmitField('Submit')


class CasesForm(FlaskForm):
    name = StringField('name',
                        validators=[DataRequired()])
    itemList = FieldList(StringField(validators=[DataRequired()]), min_entries=0)
    platform = SelectField('platform', coerce=int)
    id = StringField('id')
    submit = SubmitField('Submit')

class ButtonForm(FlaskForm):
    button = SubmitField()
    id = HiddenField()
    info = HiddenField()

class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Length(max=120)])
    password = StringField('Password', validators=[DataRequired(), Length(min=6, max=100)])
    confirm_password = StringField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    is_admin = BooleanField('Admin Privileges')
    submit = SubmitField('Add User')

class ChangePasswordForm(FlaskForm):
    new_password = StringField('New Password', validators=[DataRequired(), Length(min=6, max=100)])
    confirm_password = StringField('Confirm Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')

class CityReportForm(FlaskForm):
    state = SelectField('State', validators=[DataRequired()], choices=[], coerce=str)
    city = SelectField('City', validators=[DataRequired()], choices=[], coerce=str)
    year = SelectField('Year', choices=[], coerce=str)
    submit = SubmitField('Search by City')

class ReturnItemForm(FlaskForm):
    id = HiddenField('id')
    returned_fee = DecimalField('Returned Fee', validators=[DataRequired(), NumberRange(min=0, message='Returned fee must be a positive number')])
    return_to = HiddenField('return_to')
    submit = SubmitField('Return Item')

