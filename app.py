from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from forms import PurchaseForm, SaleForm, GroupForm, ListForm, ItemForm, ReportsForm, ExpenseForm, TimerForm
from upload_function import *
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from werkzeug.utils import secure_filename
from flask_googlemaps import GoogleMaps, Map
import random, os

import get_data, set_data
import files
import function

app = Flask(__name__)

# Initialize the extension
app.config.from_object("config.ProductionConfig")

@app.context_processor
def update_layout_with_timer():
    return dict(is_timer_running=get_data.get_active_timers_garage_sales())
  
GoogleMaps(app)
MySQL(app)

@app.route('/')
def index():
    profit = get_data.get_profit()
    return render_template('index.html', profit=profit)

@app.route('/reports/profit',methods=["GET", "POST"])
def reports_profit():
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        start_date, end_date = function.set_dates(details)
        sold_dates = get_data.get_group_sold_from_date(start_date, end_date)
        purchased_dates = get_data.get_purchased_from_date(start_date, end_date)
        return render_template('reports_profit.html', form=form, sold_dates=sold_dates, purchased_dates=purchased_dates)
    return render_template('reports_profit.html', form=form)


@app.route('/reports/sales',methods=["GET", "POST"])
def reports_sale():
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        start_date, end_date = function.set_dates(details)
        sold_dates = get_data.get_sold_from_date(start_date, end_date)
        return render_template('reports_sales.html', form=form, sold_dates=sold_dates)
    return render_template('reports_sales.html', form=form)

@app.route('/reports/purchases',methods=["GET", "POST"])
def reports_purchases():
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        start_date, end_date = function.set_dates(details)
        purchased_dates = get_data.get_purchased_from_date(start_date, end_date)
        return render_template('reports_purchases.html', form=form, purchased_dates=purchased_dates)
    return render_template('reports_purchases.html', form=form)

@app.route('/reports/categories',methods=["GET", "POST"])
def reports_categories():
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
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        start_date, end_date = function.set_dates(details)
        expense_type = int(details['expense_type'])
        expenses_dates = get_data.get_expenses_from_date(start_date, end_date, expense_type)
        return render_template('reports_expenses.html', form=form, expenses_dates=expenses_dates, expense_type=expense_type)
    return render_template('reports_expenses.html', form=form)

@app.route('/reports/locations',methods=["GET", "POST"])
def reports_locations():
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        start_date, end_date = function.set_dates(details)
        locations = get_data.get_location_from_date(start_date, end_date)
        print(locations)
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
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/expense/gas',methods=["POST","GET"])
def expense_gas():
    form = ExpenseForm()
    if request.method == "POST":
        details = request.form
        name = "%s-gas" % (details['date'])
        image_id = files.upload_image(request.files['image'])
        set_data.set_expense_gas(name, details, image_id)
        return redirect(url_for('list_expense'))
    return render_template('expense_gas.html', form=form)

@app.route('/expense/item',methods=["POST","GET"])
def expense_item():
    form = ExpenseForm()

    if request.method == "POST":
        details = request.form
        name = "%s-%s" % (details['date'], details['name'])
        image_id = files.upload_image(request.files['image'])
        set_data.set_expense_item(name, details, image_id)
        return redirect(url_for('list_expense'))
    return render_template('expense_item.html', form=form)

@app.route('/expense/store',methods=["POST","GET"])
def expense_store():
    form = ExpenseForm()

    if request.method == "POST":
        details = request.form
        name = "%s-ebay-store" % (details['date'])
        image_id = files.upload_image(request.files['image'])
        set_data.set_expense_store(name, details, image_id)
        return redirect(url_for('list_expense'))
    return render_template('expense_store.html', form=form)


@app.route('/expense/modify',methods=["POST","GET"])
def modify_expense():
    id = request.args.get('id', type = str)
    expense = get_data.get_data_for_expense_describe(id)

    form = ExpenseForm()
    form.type.data = expense[0]['type']
    print(expense[0]['type'])
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
        set_data.set_modify_expense(details,  price, milage, image_id)
        return redirect(url_for('describe_expense',id=details['id']))
    return render_template('modify_expense.html', expense=expense, form=form)

@app.route('/groups/modify',methods=["POST","GET"])
def modify_group():
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
    id = request.args.get('item', type = str)
    set_data.set_mark_sold(id)    
    return redirect(url_for('describe_item',item=id))

@app.route('/items/bought',methods=["POST","GET"])
def bought_items():
    group_id = request.args.get('group', type = int)
    groups = get_data.get_all_from_groups(None)
    categories = get_data.get_all_from_categories()

    form = PurchaseForm()
    form.group.choices = [(group['id'], group['name']) for group in groups]
    form.group.data = group_id

    if request.method == "POST":
        details = request.form
        set_data.set_bought_items(details)
        if get_data.get_timer_data_for_groups(group_id):
            set_data.end_timer_listing(group_id, datetime.now().replace(microsecond=0))
        group_data = get_data.get_all_from_group(details['group'])
        return redirect(url_for('describe_group',group_id=group_data['id']))
    return render_template('items_purchased.html', form=form)

@app.route('/items/modify',methods=["POST","GET"])
def modify_items():
    groups = get_data.get_all_from_groups(None)
    categories = get_data.get_all_from_categories()
    id = request.args.get('item', type = str)
    item = get_data.get_data_for_item_describe(id)
    sale = get_data.get_data_from_sale(id)

    form = ItemForm()
    form.group.choices = [(group['id'], group['name']) for group in groups]
    form.group.data = item[0]['group_id']

    form.category.choices = [(category['id'], category['type']) for category in categories]
    form.category.data = item[0]['category_id']

    if request.method == "POST":
        details = request.form
        set_data.set_items_modify(details)
        set_data.set_sale_data(details)
        return redirect(url_for('describe_item',item=id))
    return render_template('modify_item.html', form=form, item=item, sale=sale)

@app.route('/items/sold',methods=["POST","GET"])
def sold_items():
    item_id = request.args.get('item', type = int)
    timer = request.args.get('timer')
    items = get_data.get_all_items_not_sold()

    form = SaleForm()
    form.id.choices = [(item['id'], item['name']) for item in items]
    form.id.data = item_id

    if request.method == "POST":
        details = request.form
        set_data.set_mark_sold(details['id'])
        set_data.set_sale_data(details)
        if timer:
            set_data.end_timer_packing(details['id'], datetime.now().replace(microsecond=0))
        return redirect(url_for('describe_item',item=details['id']))
    return render_template('items_sold.html', form=form)

#List Section
@app.route('/expense/list', methods=["POST","GET"])
def list_expense():
    date = request.args.get('date', type = str)
    expenses = get_data.get_all_from_expenses(date)
    return render_template('expenses_list.html', expenses=expenses)

@app.route('/groups/list')
def groups_list():
    date = request.args.get('date', type = str)
    groups = get_data.get_all_from_group_and_items(date)
    all_groups = get_data.get_all_from_groups(date)
    return render_template('groups_list.html', groups=groups, all_groups=all_groups)

@app.route('/items/sold_list')
def sold_list():
    date = request.args.get('date', type = str)
    items = get_data.get_list_of_items_purchased_by_date(date, sold=1)
    sold = get_data.get_all_items_sold()
    return render_template('items_sold_list.html', items=items, sold=sold)

@app.route('/items/unsold_list')
def unsold_list():
    date = request.args.get('date', type = str)
    items = get_data.get_list_of_items_purchased_by_date(date, sold=0)
    return render_template('items_unsold_list.html', items=items, current_date=datetime.now().date())

#Describe Section
@app.route('/items/describe',methods=["POST","GET"])
def describe_item():
    id = request.args.get('item', type = str)

    form = TimerForm()
    form.button.label.text = "Sell Item"
    form.id.data = id

    if request.method == "POST":
        details = request.form
        set_data.start_timer_packing(details['id'], datetime.now().replace(microsecond=0))
        return redirect(url_for('sold_items',item=details['id'], timer='true'))

    item = get_data.get_data_for_item_describe(id)
    category = get_data.get_category(item[0]['category_id'])
    max_item = get_data.get_max_item_id()
    item_sold = get_data.get_data_for_item_sold(id)
    timer = get_data.get_timer_data_for_item(id)
    return render_template('items_describe.html', 
                            item=item,
                            category=category,
                            max_item=max_item,
                            sold=item_sold,
                            form=form,
                            timer=timer)

@app.route('/expense/describe')
def describe_expense():
    id = request.args.get('id', type = str)
    expense = get_data.get_data_for_expense_describe(id)
    print(expense)
    max_expense = get_data.get_max_expense_id()
    return render_template('expense_describe.html', 
                            expense=expense,
                            max_expense=max_expense)

@app.route('/groups/describe', methods=["POST","GET"])
def describe_group():
    id = request.args.get('group_id', type = str)
    group_id = get_data.get_data_from_group_describe(id)
    max_group_id = get_data.get_max_group_id()
    items = get_data.get_data_from_item_groups(id)
    sold_price = get_data.get_group_profit(id)
    if not sold_price:
        sold_price = 0

    form = TimerForm()
    form.button.label.text = "List Items"
    form.id.data = id

    if request.method == "POST":
        details = request.form
        if not get_data.get_timer_data_for_groups(details['id']):
            set_data.start_timer_listing(details['id'], datetime.now().replace(microsecond=0))
        return redirect(url_for('bought_items',group=details['id']))

    return render_template('groups_describe.html', 
                            group_id=group_id,
                            items=items,
                            max_group_id = max_group_id,
                            sold_price=sold_price,
                            form=form)

@app.route('/location', methods=["GET"])
def location():
    id = request.args.get('group_id', type = str)
    location = get_data.get_location(id)
    print(location)
    return render_template('location.html', location=location, id=id)


#Timers
@app.route('/timer/list', methods=["GET"])
def timer_list():
    timers_packing = get_data.get_timers_packing()
    timers_listing = get_data.get_timers_listing()
    timers_garage_sales = get_data.get_timers_garage_sales()
    return render_template('timer_list.html', 
                            timers_listing=timers_listing, timers_packing=timers_packing,
                            timers_garage_sales=timers_garage_sales)

@app.route('/timer/start')
def timer_start():
    active = get_data.get_active_timers_garage_sales()
    if not active:
        set_data.start_timer_saling(datetime.now().replace(microsecond=0))
    return redirect(url_for('timer_list'))
    

@app.route('/timer/end', methods=["GET"])
def timer_end():
    item = request.args.get('item', type = int)
    group = request.args.get('group', type = int)
    time = request.args.get('time')

    if(item):
        set_data.end_timer_packing(item, datetime.now().replace(microsecond=0))
    elif(group):
        set_data.end_timer_listing(group, datetime.now().replace(microsecond=0))
    else:
        set_data.end_timer_saling(time, datetime.now().replace(microsecond=0))
    return redirect(url_for('timer_list'))

if __name__ == '__main__':
    app.run(debug=True)
