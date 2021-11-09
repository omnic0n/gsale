from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from forms import PurchaseForm, SaleForm, GroupForm, ListForm, ItemForm, ReportsForm
from upload_function import *
from datetime import datetime, date
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
                    groups.name AS group_name
                    FROM items items
                    INNER JOIN groups groups ON items.group_id = groups.id
                    WHERE items.id = %s""", (item_id, ))
    return list(cur.fetchall())

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

def get_list_of_items_purchased_by_date(sold=0):
        cur = mysql.connection.cursor()
        cur.execute("""SELECT 
                    items.id, 
                    items.name, 
                    items.sold,
                    items.group_id,
                    groups.date
                    FROM items items 
                    INNER JOIN groups groups ON items.group_id = groups.id
                    WHERE items.sold = %s""",
                    (sold,))
        return list(cur.fetchall())

def set_dates(details):
    year = int(details['year'])
    month = int(details['month'])
    if(details['type'] == "Year"):
        start_date = ("%s-01-01") % (year)
        end_date = ("%s-01-01") % (year + 1)
    else:
        start_date = ("%s-%s-01") % (year, month)
        if details['month'] == 12:
            end_date = ("%s-01-01") % (year + 1)
        else:
            end_date = ("%s-%s-01") % (year, month + 1)
    
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
                    WHERE groups.date >= %s AND groups.date < %s
					GROUP BY groups.date""",
                    (start_date, end_date,))
    return list(cur.fetchall())

def get_sold_from_date(start_date, end_date):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT 
				    sale.date,
                    SUM(sale.price - sale.shipping_fee) AS net
                    FROM items items 
                    INNER JOIN sale sale ON items.id = sale.id
                    WHERE sale.date >= %s AND sale.date < %s
					GROUP BY sale.date""",
                    (start_date, end_date,))
    return list(cur.fetchall())

def get_purchased_from_date(start_date, end_date):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT
                   date,
                   SUM(price) as price
                   FROM groups
                   WHERE groups.date >= %s AND groups.date < %s
                   GROUP by date""",
                   (start_date, end_date,))
    return list(cur.fetchall())

def get_all_from_groups(date):
    cur = mysql.connection.cursor()
    if not date:
        cur.execute("SELECT * FROM groups ORDER BY name ASC")
    else:
        cur.execute("SELECT * FROM groups WHERE date LIKE %s ORDER BY name ASC", (date, ))
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
        return render_template('reports_sale.html', form=form, sold_dates=sold_dates)
    return render_template('reports_sale.html', form=form)


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

#Data Section
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
    id = request.args.get('item', type = str)
    item = get_data_for_item_describe(id)
    sale = get_data_from_sale(id)

    form = ItemForm()
    form.group.choices = [(group['id'], group['name']) for group in groups]
    form.group.data = item[0]['group_id']
    if request.method == "POST":
        details = request.form

        cur = mysql.connection.cursor()
        cur.execute("UPDATE items SET name = %s, group_id = %s where id = %s", 
                    (details['name'], details['group'], details['id']))
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
@app.route('/groups/list')
def groups_list():
    date = request.args.get('date', type = str)
    print(date)
    groups = get_all_from_group_and_items(date)
    all_groups = get_all_from_groups(date)
    return render_template('groups_list.html', groups=groups, all_groups=all_groups)

@app.route('/items/sold_list')
def sold_list():
    items = get_list_of_items_purchased_by_date(sold=1)
    sold = get_all_items_sold()
    return render_template('items_sold_list.html', items=items, sold=sold)

@app.route('/items/unsold_list')
def unsold_list():
    items = get_list_of_items_purchased_by_date(sold=0)

    return render_template('items_unsold_list.html', items=items)

#Describe Section
@app.route('/items/describe')
def describe_item():
    id = request.args.get('item', type = str)
    item = get_data_for_item_describe(id)
    max_item = get_max_item_id()
    item_sold = get_data_for_item_sold(id)
    return render_template('items_describe.html', 
                            item=item,
                            max_item=max_item,
                            sold=item_sold)

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