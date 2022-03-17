from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from forms import PurchaseForm, SaleForm, GroupForm, ListForm, ItemForm, ReportsForm, ExpenseForm
from upload_function import *
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from werkzeug.utils import secure_filename
import random, os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.secret_key = '4T3*%go^Gcn7TrYm'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'gsale'
app.config['MYSQL_PASSWORD'] = 'DR1wZcjTF7858gnu'
app.config['MYSQL_DB'] = 'gsale'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

mysql = MySQL(app)

today = date.today()
current_date = today.strftime("%Y-%m-%d")

def get_all_from_group(group_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM groups WHERE id = %s", (group_id,))
    return cur.fetchone()

def get_all_from_group_and_items(date):
    cur = mysql.connection.cursor()
    if date:
        cur.execute(""" SELECT 
                groups.name, 
                groups.price, 
                groups.id,
                groups.date,
                sum(sale.price - sale.shipping_fee) AS net 
                FROM groups groups
                RIGHT JOIN items items ON groups.id = items.group_id 
                LEFT JOIN sale sale ON sale.id = items.id
                WHERE groups.date LIKE %s
                GROUP by items.group_id
                ORDER by groups.id""", (date, ))
    else:
        cur.execute(""" SELECT 
                groups.name, 
                groups.price, 
                groups.id,
                groups.date,
                sum(sale.price - sale.shipping_fee) AS net 
                FROM groups groups
                RIGHT JOIN items items ON groups.id = items.group_id 
                LEFT JOIN sale sale ON sale.id = items.id
                GROUP by items.group_id
                ORDER by groups.id""")
    return list(cur.fetchall())

def get_all_from_items(item_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items WHERE id = %s", (item_id, ))
    return list(cur.fetchall())

def get_data_from_item_groups(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    items.name, 
                    items.sold, 
                    items.id,
                    sum(sale.price - sale.shipping_fee) AS net 
                    FROM items items
                    INNER JOIN groups groups ON items.group_id = groups.id
                    LEFT JOIN sale sale ON sale.id = items.id
                    WHERE items.group_id = %s
                    GROUP BY items.id""", (group_id, ))
    return list(cur.fetchall())

def get_all_items_not_sold():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items WHERE sold = 0 ORDER BY name ASC")
    return list(cur.fetchall())

def get_all_items_sold():
    cur = mysql.connection.cursor()    
    cur.execute("""SELECT
                    sale.id,
                    sale.date,
                    (sale.price - sale.shipping_fee) AS net
                    FROM sale
                    INNER JOIN items items ON items.id = sale.id
                    WHERE items.sold = 1""")
    return list(cur.fetchall())

def get_max_item_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM items ORDER BY id DESC LIMIT 0,1")
    return cur.fetchone()

def get_max_group_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM groups ORDER BY id DESC LIMIT 0,1")
    return cur.fetchone()

def get_data_for_item_describe(item_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    items.name, 
                    items.sold, 
                    items.id,
                    items.group_id,
                    items.category_id,
                    groups.name AS group_name
                    FROM items items
                    INNER JOIN groups groups ON items.group_id = groups.id
                    WHERE items.id = %s""", (item_id, ))
    return list(cur.fetchall())

def get_data_for_expense_describe(id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    * FROM expenses
                    WHERE id = %s""", (id, ))
    return list(cur.fetchall())

def get_max_expense_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM expenses ORDER BY id DESC LIMIT 0,1")
    return cur.fetchone()

def get_data_from_sale(item_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    date, 
                    price, 
                    shipping_fee
                    from sale
                    WHERE id = %s""", (item_id, ))
    return list(cur.fetchall())

def get_data_from_group_describe(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    groups.name, 
                    groups.price, 
                    groups.id,
                    groups.date,
                    groups.image
                    FROM groups
                    WHERE groups.id = %s""", (group_id, ))
    return list(cur.fetchall())

def get_data_for_item_sold(item_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    sale.price, 
                    sale.date,
                    sale.shipping_fee,
                    (sale.price - sale.shipping_fee) AS net
                    FROM sale sale
                    WHERE sale.id = %s""", (item_id, ))
    return list(cur.fetchall())

def get_list_of_items_purchased_by_date(date, sold=0):
        cur = mysql.connection.cursor()
        if date:
            cur.execute("""SELECT 
                        items.id, 
                        items.name, 
                        items.sold,
                        items.group_id,
                        sale.date as sales_date,
                        groups.date
                        FROM items items 
                        INNER JOIN groups groups ON items.group_id = groups.id
                        INNER JOIN sale sale on items.id = sale.id
                        WHERE sale.date = %s""", (date,))
        else:    
            cur.execute("""SELECT 
                        items.id, 
                        items.name, 
                        items.sold,
                        items.group_id,
                        sale.date as sales_date,
                        groups.date
                        FROM items items 
                        INNER JOIN groups groups ON items.group_id = groups.id
                        INNER JOIN sale sale on items.id = sale.id
                        WHERE items.sold = %s""",
                        (sold,))
        return list(cur.fetchall())

def get_list_of_items_with_categories(category_id):
        cur = mysql.connection.cursor()
        cur.execute("""SELECT 
                    items.id, 
                    items.name, 
                    items.sold,
                    items.group_id,
                    categories.type,
                    categories.id AS category_id,
                    sale.date as sales_date,
                    groups.date
                    FROM items items 
                    INNER JOIN groups groups ON items.group_id = groups.id
                    INNER JOIN sale sale ON items.id = sale.id
                    INNER JOIN categories categories ON items.category_id = categories.id
                    WHERE categories.id = %s
                    ORDER BY categories.id""",
                    (category_id,))
        return list(cur.fetchall())

def set_dates(details):
    year = int(details['year'])
    month = int(details['month'])
    date = details['date']
    if(details['type'] == "Year"):
        print("year")
        start_date = ("%s-01-01") % (year)
        end_date = datetime.strptime(("%s-01-01") % (year + 1), '%Y-%m-%d').date() - timedelta(days=1)
    elif(details['type'] == "Month"):
        print("month")
        start_date = ("%s-%s-01") % (year, month)
        end_date = datetime.strptime(("%s-%s-01") % (year,month),'%Y-%m-%d').date() + relativedelta(months=1) - timedelta(days=1)
    else:
        start_date = date
        end_date = date

    print(details)
    print(start_date)
    print(end_date)
    return start_date, end_date

def get_group_sold_from_date(start_date, end_date):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT 
				    groups.date,
                    SUM(sale.price - sale.shipping_fee) AS net
                    FROM items items 
                    INNER JOIN sale sale ON items.id = sale.id
                    INNER JOIN groups groups ON items.group_id = groups.id
                    WHERE groups.date >= %s AND groups.date <= %s GROUP BY groups.date""",
                    (start_date, end_date,))
    return list(cur.fetchall())

def get_sold_from_date(start_date, end_date):
    print(start_date)
    print(end_date)
    cur = mysql.connection.cursor()
    cur.execute("""SELECT 
				    sale.date,
                    SUM(sale.price) as price,
                    SUM(sale.shipping_fee) as shipping_fee,
                    SUM(sale.price - sale.shipping_fee) AS net
                    FROM items items 
                    INNER JOIN sale sale ON items.id = sale.id
                    WHERE sale.date >= %s AND sale.date <= %s GROUP BY sale.date""",
                    (start_date, end_date,))
    return list(cur.fetchall())

def get_purchased_from_date(start_date, end_date):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT
                   date,
                   SUM(price) as price
                   FROM groups
                   WHERE groups.date >= %s AND groups.date <= %s GROUP by date""",
                   (start_date, end_date,))
    return list(cur.fetchall())

def get_expenses_from_date(start_date, end_date, type):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT 
				    * FROM expenses
                    WHERE date >= %s AND date <= %s
                    AND type = %s
					ORDER BY date""",
                    (start_date, end_date, type,))
    return list(cur.fetchall())

def get_all_from_groups(date):
    cur = mysql.connection.cursor()
    if not date:
        cur.execute("SELECT * FROM groups ORDER BY name ASC")
    else:
        cur.execute("SELECT * FROM groups WHERE date LIKE %s ORDER BY name ASC", (date, ))
    return list(cur.fetchall())

def get_all_from_categories():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categories")
    return list(cur.fetchall())

def get_category(category_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT type FROM categories where id = %s", (category_id, ))
    return cur.fetchone()

def get_all_from_expenses(date):
    cur = mysql.connection.cursor()
    if not date:
        cur.execute("SELECT * FROM expenses ORDER BY name ASC")
    else:
        cur.execute("SELECT * FROM expenses WHERE date LIKE %s ORDER BY name ASC", (date, ))
    return list(cur.fetchall())

def get_profit():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT SUM(tbl.price) AS price
                FROM (SELECT price FROM groups) tbl""")
    purchase = list(cur.fetchall())
    cur.execute("SELECT sum((sale.price - sale.shipping_fee)) AS price FROM sale")
    sale = list(cur.fetchall())
    return sale[0]['price'],purchase[0]['price']

def get_group_profit(group_id):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT sum((sale.price - sale.shipping_fee)) 
                AS price FROM sale 
                WHERE id IN 
                    (SELECT id FROM items 
                     WHERE sold = 1 
                     AND group_id = %s)""", (group_id, ))
    sale = list(cur.fetchall())
    return sale[0]['price']


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image(file):
    filename = str(random.getrandbits(128)) + '.jpg'
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename)))
    return filename

@app.route('/')
def index():
    profit = get_profit()
    return render_template('index.html', profit=profit)

@app.route('/reports/profit',methods=["GET", "POST"])
def reports_profit():
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        start_date, end_date = set_dates(details)
        sold_dates = get_group_sold_from_date(start_date, end_date)
        purchased_dates = get_purchased_from_date(start_date, end_date)
        return render_template('reports_profit.html', form=form, sold_dates=sold_dates, purchased_dates=purchased_dates)
    return render_template('reports_profit.html', form=form)


@app.route('/reports/sales',methods=["GET", "POST"])
def reports_sale():
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        start_date, end_date = set_dates(details)
        sold_dates = get_sold_from_date(start_date, end_date)
        return render_template('reports_sales.html', form=form, sold_dates=sold_dates)
    return render_template('reports_sales.html', form=form)

@app.route('/reports/purchases',methods=["GET", "POST"])
def reports_purchases():
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        start_date, end_date = set_dates(details)
        purchased_dates = get_purchased_from_date(start_date, end_date)
        return render_template('reports_purchases.html', form=form, purchased_dates=purchased_dates)
    return render_template('reports_purchases.html', form=form)

@app.route('/reports/categories',methods=["GET", "POST"])
def reports_categories():
    form = ReportsForm()

    categories = get_all_from_categories()
    form.category.choices = [(category['id'], category['type']) for category in categories]

    if request.method == "POST":
        details = request.form
        item_categories = get_list_of_items_with_categories(details['category_id'])
        return render_template('reports_item_categories.html', form=form, item_categories=item_categories)
    return render_template('reports_item_categories.html', form=form)

@app.route('/reports/expenses',methods=["GET", "POST"])
def reports_expenses():
    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        start_date, end_date = set_dates(details)
        expense_type = int(details['expense_type'])
        expenses_dates = get_expenses_from_date(start_date, end_date, expense_type)
        return render_template('reports_expenses.html', form=form, expenses_dates=expenses_dates, expense_type=expense_type)
    return render_template('reports_expenses.html', form=form)

#Data Section
@app.route('/groups/create',methods=["POST","GET"])
def group_add():
    form = GroupForm()

    if request.method == "POST":
        details = request.form
        group_name = "%s-%s" % (details['date'],details['name'])
        if(request.files['image']):
            image_id = upload_image(request.files['image'])
        else:
            image_id = 'NULL'
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO groups(name, date, price,image) VALUES (%s, %s, %s, %s)", 
                   (group_name, details['date'], details['price'], image_id))
        mysql.connection.commit()
        group_id = str(cur.lastrowid)
        cur.close()
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
        if(request.files['image']):
            image_id = upload_image(request.files['image'])
        else:
            image_id = 'NULL'
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO expenses(name, date, milage, image, type) VALUES (%s, %s, %s, %s, %s)", 
                   (name, details['date'], details['milage'], image_id, 1))
        mysql.connection.commit()
        id = str(cur.lastrowid)
        cur.close()
        return redirect(url_for('list_expense'))
    return render_template('expense_gas.html', form=form)

@app.route('/expense/item',methods=["POST","GET"])
def expense_item():
    form = ExpenseForm()

    if request.method == "POST":
        details = request.form
        name = "%s-%s" % (details['date'], details['name'])
        if(request.files['image']):
            image_id = upload_image(request.files['image'])
        else:
            image_id = 'NULL'
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO expenses(name, date, price, image, type) VALUES (%s, %s, %s, %s, %s)", 
                   (name, details['date'], details['price'], image_id, 2))
        mysql.connection.commit()
        id = str(cur.lastrowid)
        cur.close()
        return redirect(url_for('list_expense'))
    return render_template('expense_item.html', form=form)

@app.route('/expense/modify',methods=["POST","GET"])
def modify_expense():
    id = request.args.get('id', type = str)
    expense = get_data_for_expense_describe(id)

    form = ExpenseForm()
    form.type.data = expense[0]['type']

    if request.method == "POST":
        details = request.form
        if(request.files['image']):
            image_id = upload_image(request.files['image'])
        else:
            image_id = 'NULL'
        
        if(expense[0]['type'] == 1):
            price = 0
            milage = details['milage']
        else:
            price = details['price']
            milage = 0

        cur = mysql.connection.cursor()
        cur.execute("UPDATE expenses SET name = %s, date = %s, price = %s, milage = %s, type = %s, image = %s where id = %s", 
                    (details['name'], details['date'], price, milage, details['type'], image_id, details['id']))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('describe_expense',id=details['id']))
    return render_template('modify_expense.html', expense=expense, form=form)

@app.route('/groups/modify',methods=["POST","GET"])
def modify_group():
    id = request.args.get('group_id', type = str)
    group_id = get_data_from_group_describe(id)

    form = GroupForm()

    if request.method == "POST":
        details = request.form
        if(request.files['image']):
            image_id = upload_image(request.files['image'])
        else:
            image_id = 'NULL'
        cur = mysql.connection.cursor()
        cur.execute("UPDATE groups SET name = %s, date = %s, price = %s, image = %s where id = %s", 
                    (details['name'], details['date'], details['price'], image_id, details['id']))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('describe_group',group_id=details['id']))
    return render_template('modify_group.html', group_id=group_id, form=form)

@app.route('/items/mark_sold',methods=["POST","GET"])
def mark_sold():
    id = request.args.get('item', type = str)
    print(id)
    cur = mysql.connection.cursor()
    cur.execute("UPDATE items SET sold = 1 where id = %s", 
                (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('describe_item',item=id))

@app.route('/items/bought',methods=["POST","GET"])
def bought_items():
    groups = get_all_from_groups(None)

    form = PurchaseForm()
    form.group.choices = [(group['id'], group['name']) for group in groups]
    if request.method == "POST":
        details = request.form

        cur = mysql.connection.cursor()
        for item in details['name'].splitlines():
            cur.execute("INSERT INTO items(name, group_id) VALUES (%s, %s)", 
                        (item,details['group'],))
            mysql.connection.commit()
            item_id = str(cur.lastrowid)
            cur.execute("INSERT INTO sale(id, price, shipping_fee, date) VALUES (%s, 0, 0, %s)",
                        (item_id,current_date,))
            mysql.connection.commit()
            group_data = get_all_from_group(details['group'])
        cur.close()
        return redirect(url_for('describe_group',group_id=group_data['id']))
    return render_template('items_purchased.html', form=form)

@app.route('/items/modify',methods=["POST","GET"])
def modify_items():
    groups = get_all_from_groups(None)
    categories = get_all_from_categories()
    id = request.args.get('item', type = str)
    item = get_data_for_item_describe(id)
    sale = get_data_from_sale(id)

    form = ItemForm()
    form.group.choices = [(group['id'], group['name']) for group in groups]
    form.group.data = item[0]['group_id']

    form.category.choices = [(category['id'], category['type']) for category in categories]
    form.category.data = item[0]['category_id']

    if request.method == "POST":
        details = request.form

        cur = mysql.connection.cursor()
        cur.execute("UPDATE items SET name = %s, group_id = %s, category_id =%s where id = %s", 
                    (details['name'], details['group'], details['category'], details['id']))
        mysql.connection.commit()
        cur.execute("UPDATE sale SET price = %s, shipping_fee = %s, date = %s where id = %s", 
                    (details['price'], details['shipping_fee'], details['date'], details['id']))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('describe_item',item=id))
    return render_template('modify_item.html', form=form, item=item, sale=sale)

@app.route('/items/sold',methods=["POST","GET"])
def sold_items():
    items = get_all_items_not_sold()

    form = SaleForm()
    form.name.choices = [(item['id'], item['name']) for item in items]
    if request.method == "POST":
        details = request.form
        cur = mysql.connection.cursor()
        cur.execute("UPDATE items SET sold = 1 WHERE id = %s", (details['name'], ))
        cur.execute("UPDATE sale SET date = %s, price = %s, shipping_fee = %s WHERE id = %s", 
                    (details['date'], details['price'], details['shipping_fee'], details['name'],))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('describe_item',item=details['name']))
    return render_template('items_sold.html', form=form)

#List Section
@app.route('/expense/list',methods=["POST","GET"])
def list_expense():
    date = request.args.get('date', type = str)
    expenses = get_all_from_expenses(date)
    return render_template('expenses_list.html', expenses=expenses)

@app.route('/groups/list')
def groups_list():
    date = request.args.get('date', type = str)
    groups = get_all_from_group_and_items(date)
    all_groups = get_all_from_groups(date)
    return render_template('groups_list.html', groups=groups, all_groups=all_groups)

@app.route('/items/sold_list')
def sold_list():
    date = request.args.get('date', type = str)
    items = get_list_of_items_purchased_by_date(date, sold=1)
    print(items)
    sold = get_all_items_sold()
    return render_template('items_sold_list.html', items=items, sold=sold)

@app.route('/items/unsold_list')
def unsold_list():
    date = request.args.get('date', type = str)
    items = get_list_of_items_purchased_by_date(date, sold=0)
    return render_template('items_unsold_list.html', items=items)

#Describe Section
@app.route('/items/describe')
def describe_item():
    id = request.args.get('item', type = str)
    item = get_data_for_item_describe(id)
    category = get_category(item[0]['category_id'])
    max_item = get_max_item_id()
    item_sold = get_data_for_item_sold(id)
    return render_template('items_describe.html', 
                            item=item,
                            category=category,
                            max_item=max_item,
                            sold=item_sold)

@app.route('/expense/describe')
def describe_expense():
    id = request.args.get('id', type = str)
    expense = get_data_for_expense_describe(id)
    print(expense)
    max_expense = get_max_expense_id()
    return render_template('expense_describe.html', 
                            expense=expense,
                            max_expense=max_expense)

@app.route('/groups/describe')
def describe_group():
    id = request.args.get('group_id', type = str)
    group_id = get_data_from_group_describe(id)
    max_group_id = get_max_group_id()
    items = get_data_from_item_groups(id)
    sold_price = get_group_profit(id)
    if not sold_price:
        sold_price = 0

    return render_template('groups_describe.html', 
                            group_id=group_id,
                            items=items,
                            max_group_id = max_group_id,
                            sold_price=sold_price)

if __name__ == '__main__':
    app.run(debug=True)