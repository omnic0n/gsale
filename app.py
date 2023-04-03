from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_mysqldb import MySQL
from forms import PurchaseForm, SaleForm, GroupForm, ListForm, ItemForm, ReportsForm, ExpenseForm, ButtonForm, CasesForm
from upload_function import *
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from werkzeug.utils import secure_filename
from flask_session import Session
import random, os, math

import get_data, set_data
import files
import function
import config

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize the extension
app.config.from_object("config.ProductionConfig")

MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        addr = request.environ['HTTP_X_FORWARDED_FOR'].split(',')
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        msg = function.login_data(username=username, password=password, ip=addr[0])
        if 'loggedin' in session:
            return redirect(url_for('index'))    
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/')
def index():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  

    items = []
    years = get_data.get_years()
   
    for value in years:
        item = get_data.get_profit(value['year'])
        items.append(item)
    return render_template('index.html', items=items)

@app.route('/reports/profit',methods=["GET", "POST"])
def reports_profit():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  

    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        start_date, end_date = function.set_dates(details)
        sold_dates = get_data.get_group_sold_from_date(start_date, end_date)
        purchased_dates = get_data.get_purchased_from_date(start_date, end_date)
        expenses= get_data.get_all_from_expenses_date(start_date, end_date)
        return render_template('reports_profit.html', form=form, sold_dates=sold_dates, purchased_dates=purchased_dates, expenses=expenses,type_value=details['type'])
    return render_template('reports_profit.html', form=form)


@app.route('/reports/sales',methods=["GET", "POST"])
def reports_sale():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
        
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        if not details['type'] == '3':
            start_date, end_date = function.set_dates(details)
            sold_dates = get_data.get_sold_from_date(start_date, end_date)
        else:
            sold_dates = get_data.get_sold_from_day(details['day'])
        return render_template('reports_sales.html', form=form, sold_dates=sold_dates,type_value=details['type'])
    return render_template('reports_sales.html', form=form)

@app.route('/reports/purchases',methods=["GET", "POST"])
def reports_purchases():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    form = ReportsForm()

    if request.method == "POST":
        details = request.form

        if not details['type'] == '3':
            start_date, end_date = function.set_dates(details)
            purchased_dates = get_data.get_purchased_from_date(start_date, end_date)
        else:
            purchased_dates = get_data.get_purchased_from_day(details['day'])

        return render_template('reports_purchases.html', form=form, purchased_dates=purchased_dates, type_value=details['type'])
    return render_template('reports_purchases.html', form=form)

@app.route('/reports/categories',methods=["GET", "POST"])
def reports_categories():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    form = ReportsForm()

    categories = get_data.get_all_from_categories()
    form.category.choices = [(category['id'], category['type']) for category in categories]

    if request.method == "POST":
        details = request.form
        item_categories = get_data.get_list_of_items_with_categories(details['category'])
        return render_template('reports_item_categories.html', form=form, item_categories=item_categories, now=datetime.now().date())
    return render_template('reports_item_categories.html', form=form)

@app.route('/reports/expenses',methods=["GET", "POST"])
def reports_expenses():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    expense_choices = get_data.get_expenses_choices()

    form = ReportsForm()
    form.expense_type.choices = [(expense_choice['id'], expense_choice['type']) for expense_choice in expense_choices]
   
    if request.method == "POST":
        details = request.form
        start_date, end_date = function.set_dates(details)
        expense_type = int(details['expense_type'])
        expenses_dates = get_data.get_expenses_from_date(start_date, end_date, expense_type)
        return render_template('reports_expenses.html', form=form, expenses_dates=expenses_dates, expense_type=expense_type)
    return render_template('reports_expenses.html', form=form)

@app.route('/reports/locations',methods=["GET", "POST"])
def reports_locations():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        start_date, end_date = function.set_dates(details)
        locations = get_data.get_location_from_date(start_date, end_date)
        map = Map(
            identifier="test",
            lat=locations[0]['latitude'],
            lng=locations[0]['longitude'],
            markers=[(loc['latitude'], loc['longitude'], "<a href=/groups/describe?group_id=%s>%s</a>" % (loc['id'], loc['name'])) for loc in locations],
            style="height:800px;width:800px"
        )
        return render_template('reports_locations.html', form=form, map=map)
    return render_template('reports_locations.html', form=form)

#Data Section
@app.route('/groups/create',methods=["POST","GET"])
def group_add():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    form = GroupForm()

    if request.method == "POST":
        details = request.form
        group_name = "%s-%s" % (details['date'],details['name'])
        image_id = files.upload_image(request.files['image'])
        group_id = set_data.set_group_add(group_name, details, image_id)
        return redirect(url_for('describe_group',group_id=group_id))
    return render_template('groups_add.html', form=form)

@app.route('/display/<filename>')
def display_image(filename):
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/expense/gas',methods=["POST","GET"])
def expense_gas():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    form = ExpenseForm()
    if request.method == "POST":
        details = request.form
        name = "%s-gas" % (details['date'])
        image_id = files.upload_image(request.files['image'])
        set_data.set_expense(name, details, image_id, 1)
        return redirect(url_for('list_expense'))
    return render_template('expense_gas.html', form=form)

@app.route('/expense/item',methods=["POST","GET"])
def expense_item():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    form = ExpenseForm()

    if request.method == "POST":
        details = request.form
        name = "%s-%s" % (details['date'], details['name'])
        image_id = files.upload_image(request.files['image'])
        set_data.set_expense(name, details, image_id, 2)
        return redirect(url_for('list_expense'))
    return render_template('expense_item.html', form=form)

@app.route('/expense/store',methods=["POST","GET"])
def expense_store():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    form = ExpenseForm()

    if request.method == "POST":
        details = request.form
        name = "%s-ebay-store" % (details['date'])
        image_id = files.upload_image(request.files['image'])
        set_data.set_expense(name, details, image_id, 3)
        return redirect(url_for('list_expense'))
    return render_template('expense_store.html', form=form)


@app.route('/expense/modify',methods=["POST","GET"])
def modify_expense():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    id = request.args.get('id', type = str)
    expense = get_data.get_data_for_expense_describe(id)
    expense_choices = get_data.get_expenses_choices()
 
    form = ExpenseForm()
    form.expense_type.choices = [(expense_choice['id'], expense_choice['type']) for expense_choice in expense_choices]
    form.expense_type.data = expense[0]['type']

    if request.method == "POST":
        details = request.form
        if(request.files['image']):
            image_id = files.upload_image(request.files['image'])
        else:
            image_id = expense[0]['image']

        if(expense[0]['type'] == 1):
            price = 0
            milage = details['milage']
        else:
            price = details['price']
            milage = 0
        set_data.set_modify_expense(details, price, milage, image_id)
        return redirect(url_for('describe_expense',id=details['id']))
    return render_template('modify_expense.html', expense=expense, form=form)

@app.route('/groups/modify',methods=["POST","GET"])
def modify_group():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    id = request.args.get('group_id', type = str)
    group_id = get_data.get_data_from_group_describe(id)

    form = GroupForm()

    if request.method == "POST":
        details = request.form
        if(request.files['image']):
            image_id = files.upload_image(request.files['image'])
        else:
            image_id = group_id[0]['image']
        set_data.set_group_modify(details, image_id)
        return redirect(url_for('describe_group',group_id=details['id']))
    return render_template('modify_group.html', group_id=group_id, form=form)

@app.route('/items/mark_sold',methods=["POST","GET"])
def mark_sold():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    id = request.args.get('item', type = str)
    set_data.set_mark_sold(id)    
    return redirect(url_for('describe_item',item=id))

@app.route('/items/mark_unsold',methods=["POST","GET"])
def mark_unsold():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    id = request.args.get('item', type = str)
    set_data.set_unmark_sold(id)    
    return redirect(url_for('describe_item',item=id))

@app.route('/items/bought',methods=["POST","GET"])
def bought_items():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    group_id = request.args.get('group', type = str)
    groups = get_data.get_all_from_groups('%')
    categories = get_data.get_all_from_categories()

    form = PurchaseForm()
    form.group.choices = [(group['id'], group['name']) for group in groups]
    form.group.data = group_id

    form.category.choices = [(category['id'], category['type']) for category in categories]

    if request.method == "POST":
        details = request.form
        set_data.set_bought_items(details)
        group_data = get_data.get_all_from_group(details['group'])
        return redirect(url_for('describe_group',group_id=group_data['id']))
    return render_template('items_purchased.html', form=form)

@app.route('/items/modify',methods=["POST","GET"])
def modify_items():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    groups = get_data.get_all_from_groups('%')
    categories = get_data.get_all_from_categories()
    id = request.args.get('item', type = str)
    item = get_data.get_data_for_item_describe(id)
    sale = get_data.get_data_from_sale(id)

    form = ItemForm()
    form.group.choices = [(group['id'], group['name']) for group in groups]
    form.group.data = item[0]['group_id']

    form.category.choices = [(category['id'], category['type']) for category in categories]
    form.category.data = item[0]['category_id']

    form.returned.choices = [(0, 'False'), (1, "True")]
    form.returned.data = item[0]['returned']

    if request.method == "POST":
        details = request.form
        set_data.set_items_modify(details)
        set_data.set_sale_data(details)
        return redirect(url_for('describe_item',item=id))
    return render_template('modify_item.html', form=form, item=item, sale=sale)

@app.route('/items/remove',methods=["POST","GET"])
def items_remove():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  

    id = request.args.get('id', type = str)
    item=get_data.get_group_id(id)
    set_data.remove_item_data(id)
    return redirect(url_for('describe_group',group_id=item['group_id']))


@app.route('/items/quick_sell',methods=["POST","GET"])
def quick_sell():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    groups = get_data.get_all_from_groups('%')
    categories = get_data.get_all_from_categories()

    form = ItemForm()
    form.group.choices = [(group['id'], group['name']) for group in groups]

    form.category.choices = [(category['id'], category['type']) for category in categories]

    if request.method == "POST":
        details = request.form
        id = set_data.set_quick_sale(details)
        return redirect(url_for('describe_item',item=id))
    return render_template('quick_sell.html', form=form)


@app.route('/items/sold',methods=["POST","GET"])
def sold_items():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    item_id = request.args.get('item', type = str)
    items = get_data.get_all_items_not_sold()

    form = SaleForm()
    form.id.choices = [(item['id'], item['name']) for item in items]
    form.id.data = item_id

    if request.method == "POST":
        details = request.form
        set_data.set_mark_sold(details['id'])
        set_data.set_sale_data(details)
        return redirect(url_for('describe_item',item=details['id']))
    return render_template('items_sold.html', form=form)

#List Section
@app.route('/expense/list', methods=["POST","GET"])
def list_expense():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    date = request.args.get('date', type = str)
    expenses = get_data.get_all_from_expenses(date)
    return render_template('expenses_list.html', expenses=expenses)

@app.route('/groups/list', methods=["POST","GET"])
def groups_list():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    form = GroupForm()

    if request.method == "POST":
        details = request.form
        date = details['listYear'] + "-%-%"
    else:
        date = request.args.get('date', type = str)

    groups = get_data.get_all_from_group_and_items(date)
    return render_template('groups_list.html', groups=groups, form=form)

@app.route('/items/sold_list', methods=["POST","GET"])
def sold_list():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    min_list = 0
    max_list = 249
    
    date = request.args.get('date', type = str)
    items = get_data.get_list_of_items_purchased_by_date(date, sold=1)
    sold = get_data.get_all_items_sold()
    page = request.args.get('page', type = int, default = 1)

    pages = int(math.ceil(float(len(items))/250))

    if page >= 1:
        min_list = (page - 1) * 250
        max_list = min_list + 249
    
    if (page * 250) < (len(items)):
        max_reached = 1
    else:
        max_reached = 0

    return render_template('items_sold_list.html', 
                            items=items, sold=sold, page=page, min_list=min_list, max_list=max_list, max_reached=max_reached, pages=pages)

@app.route('/items/unsold_list')
def unsold_list():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    date = request.args.get('date', type = str)
    items = get_data.get_list_of_items_purchased_by_date(date, sold=0)
    return render_template('items_unsold_list.html', items=items, current_date=datetime.now().date())

#Search Section
@app.route('/items/search', methods=["POST","GET"])
def items_search():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    form = ItemForm()

    if request.method == "POST":
        details = request.form
        items = get_data.get_list_of_items_with_name(details['name'])
        return render_template('items_search.html', form=form, items=items)
    return render_template('items_search.html', form=form)

#Describe Section
@app.route('/items/describe',methods=["POST","GET"])
def describe_item():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    id = request.args.get('item', type = str)

    form = ButtonForm()
    form.button.label.text = "Sell Item"
    form.id.data = id

    remove = ButtonForm()
    remove.button.label.text = "Remove Item"
    remove.id.data = id

    if request.method == "POST":
        details = request.form
        if details['button'] == "Sell Item":
            return redirect(url_for('sold_items',item=details['id']))
        elif details['button'] == "Remove Item":
            return redirect(url_for('items_remove',id=details['id']))

    item = get_data.get_data_for_item_describe(id)
    category = get_data.get_category(item[0]['category_id'])
    item_sold = get_data.get_data_for_item_sold(id)
    return render_template('items_describe.html', 
                            item=item,
                            category=category,
                            sold=item_sold,
                            form=form,
                            remove=remove)

@app.route('/expense/describe')
def describe_expense():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    id = request.args.get('id', type = str)
    expense = get_data.get_data_for_expense_describe(id)
    max_expense = get_data.get_max_expense_id()
    return render_template('expense_describe.html', 
                            expense=expense,
                            max_expense=max_expense)

@app.route('/groups/describe', methods=["POST","GET"])
def describe_group():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    id = request.args.get('group_id', type = str)
    group_id = get_data.get_data_from_group_describe(id)
    items = get_data.get_data_from_item_groups(id)
    total_items = get_data.get_total_items_in_group(id)
    sold_price = get_data.get_group_profit(id)
    if not sold_price:
        sold_price = 0

    form = ButtonForm()
    form.button.label.text = "List Items"
    form.id.data = id

    if request.method == "POST":
        details = request.form
        return redirect(url_for('bought_items',group=details['id']))

    return render_template('groups_describe.html', 
                            group_id=group_id,
                            items=items,
                            total_items=total_items,
                            sold_price=sold_price,
                            form=form)

@app.route('/location', methods=["GET"])
def location():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    id = request.args.get('group_id', type = str)
    location = get_data.get_location(id)
    return render_template('location.html', location=location, id=id)


#Cases

#List Section
@app.route('/cases/list', methods=["POST","GET"])
def cases_list():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    platform = request.args.get('platform', type = int)

    cases = get_data.get_all_from_cases(platform)
    return render_template('cases_list.html', cases=cases)

@app.route('/cases/add',methods=["POST","GET"])
def cases_add():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    platforms = get_data.get_all_from_platforms()

    form = CasesForm()
    form.platform.choices = [(platform['id'], platform['name']) for platform in platforms]
    
    if request.method == "POST":
        details = request.form
        set_data.add_case_data(details)
        return redirect(url_for('cases_list'))
    return render_template('case_add.html', form=form)

@app.route('/cases/remove',methods=["POST","GET"])
def cases_remove():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  

    id = request.args.get('id', type = str)
    set_data.remove_case_data(id)
    return redirect(url_for('cases_list'))

@app.route('/cases/modify',methods=["POST","GET"])
def modify_case():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    platforms = get_data.get_all_from_platforms()
    id = request.args.get('id', type = str)
    case = get_data.get_data_for_case_describe(id)

    form = CasesForm()
    form.platform.choices = [(platform['id'], platform['name']) for platform in platforms]
    form.platform.data = case[0]['platform_id']

    if request.method == "POST":
        details = request.form
        set_data.set_cases_modify(details)
        return redirect(url_for('cases_list'))
    return render_template('cases_modify.html', form=form, case=case)


#Search Section
@app.route('/cases/search', methods=["POST","GET"])
def cases_search():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  
     
    form = CasesForm()

    if request.method == "POST":
        details = request.form
        cases = get_data.get_list_of_cases_with_name(details['name'])
        return render_template('cases_search.html', form=form, cases=cases)
    return render_template('cases_search.html', form=form)


if __name__ == '__main__':
    app.run(debug=True, port=app.config['PORT'])
