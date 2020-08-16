from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from forms import PurchaseForm, PurchaseFormBulk, SaleForm, GroupForm, ListForm
from datetime import datetime


app = Flask(__name__)

app.secret_key = '4T3*%go^Gcn7TrYm'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'gsale'
app.config['MYSQL_PASSWORD'] = 'DR1wZcjTF7858gnu'
app.config['MYSQL_DB'] = 'gsale'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def get_long_name_location_from_id(location_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT long_name FROM location WHERE id = %s", (location_id,))
    return cur.fetchone()['long_name']

def get_name_location_from_id(location_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT name FROM location WHERE id = %s", (location_id,))
    return cur.fetchone()['name']

def get_all_from_group(group_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM groups WHERE id = %s", (group_id,))
    return cur.fetchone()

def get_all_from_items(item_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items WHERE id = %s", (item_id, ))
    return list(cur.fetchall())

def get_data_from_item_groups(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    items.name, 
                    items.sold, 
                    items.id 
                    FROM items items
                    INNER JOIN groups groups ON items.group_id = groups.id 
                    INNER JOIN location location ON groups.location = location.id
                    WHERE items.group_id = %s""", (group_id, ))
    return list(cur.fetchall())

def get_all_items_not_sold():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items WHERE sold = 0 ORDER BY name ASC")
    return list(cur.fetchall())

def get_data_for_item_describe(item_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    items.name, 
                    items.sold, 
                    items.id,
                    items.group_id, 
                    purchase.price, 
                    purchase.date, 
                    location.long_name AS location 
                    FROM items items
                    INNER JOIN purchase purchase ON purchase.id = items.id
                    INNER JOIN location location ON purchase.location = location.id
                    WHERE items.id = %s""", (item_id, ))
    return list(cur.fetchall())

def get_data_from_group_describe(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    groups.name, 
                    groups.price, 
                    groups.id,
                    groups.date,
                    location.long_name AS location 
                    FROM groups groups
                    INNER JOIN location location ON groups.location = location.id
                    WHERE groups.id = %s""", (group_id, ))
    return list(cur.fetchall())

def get_data_for_item_sold(item_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    sale.price, 
                    sale.tax,
                    sale.date, 
                    sale.ebay_fee,
                    sale.paypal_fee,
                    sale.shipping_fee,
                    (sale.price - sale.ebay_fee - sale.paypal_fee - sale.shipping_fee) AS net,
                    location.long_name as location 
                    FROM sale sale
                    INNER JOIN location location ON sale.location = location.id
                    WHERE sale.id = %s""", (item_id, ))
    return list(cur.fetchall())

def get_list_of_items_purchased_by_date(start_date='',end_date='',sold=0):
        if not start_date:
            start_date = '1969-01-01'
        if not end_date:
            end_date = '3000-01-01'

        cur = mysql.connection.cursor()
        cur.execute("""SELECT 
                    items.id, 
                    items.name, 
                    items.sold,
                    items.group_id,
                    purchase.date
                    FROM items items 
                    INNER JOIN purchase purchase ON items.id = purchase.id
                    WHERE purchase.date > %s AND purchase.date < %s AND items.sold = %s""",
                    (start_date,end_date,sold,))
        return list(cur.fetchall())

def get_all_from_locations():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM location ORDER BY name ASC")
    return list(cur.fetchall())

def get_all_from_groups():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM groups ORDER BY name ASC")
    return list(cur.fetchall())

def get_profit():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT SUM(tbl.price) AS price
                FROM (SELECT price FROM purchase
                UNION ALL
                SELECT price FROM groups) tbl""")
    purchase = list(cur.fetchall())
    cur.execute("SELECT sum((sale.price - sale.ebay_fee - sale.paypal_fee - sale.shipping_fee)) AS price FROM sale")
    sale = list(cur.fetchall())
    return sale[0]['price'],purchase[0]['price']

def get_group_profit(group_id):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT sum((sale.price - sale.ebay_fee - sale.paypal_fee - sale.shipping_fee)) 
                AS price FROM sale 
                WHERE id IN 
                    (SELECT id FROM items 
                     WHERE sold = 1 
                     AND group_id = %s)""", (group_id, ))
    sale = list(cur.fetchall())
    return sale[0]['price']

@app.route('/')
def index():
    profit = get_profit()
    return render_template('index.html', profit=profit)

#Data Section
@app.route('/groups/create',methods=["POST","GET"])
def group_add():
    locations = get_all_from_locations()

    form = GroupForm()
    form.location.choices = [(location['id'], location['long_name']) for location in locations]
    if request.method == "POST":
        details = request.form
        cur = mysql.connection.cursor()
        location = get_name_location_from_id(details['location'])
        group_name = "%s-%s-%s" % (details['date'],location,details['name'])
        cur.execute("INSERT INTO groups(name, date, price,location) VALUES (%s, %s, %s, %s)", 
                    (group_name, details['date'], details['price'], details['location']))
        mysql.connection.commit()
        group_id = str(cur.lastrowid)
        cur.close()
        return redirect(url_for('describe_group',group_id=group_id))
    return render_template('groups_add.html', form=form)


@app.route('/items/bought',methods=["POST","GET"])
def bought_items():
    locations = get_all_from_locations()
    groups = get_all_from_groups()

    form = PurchaseForm()
    form.location.choices = [(location['id'], location['long_name']) for location in locations]
    form.group.choices = [(group['id'], group['name']) for group in groups]
    if request.method == "POST":
        details = request.form
        if 'not_selling' in request.form:
            not_selling = 2
        else:
            not_selling = 0
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO items(name, group_id, sold) VALUES (%s, %s, %s)", 
                    (details['name'],details['group'],not_selling,))
        mysql.connection.commit()
        item_id = str(cur.lastrowid)
        if details['group'] == "1":
            cur.execute("INSERT INTO purchase(id, location, date, price) VALUES (%s, %s, %s, %s)", 
                        (item_id, details['location'], details['date'], details['price'],))
        else:
            group_data = get_all_from_group(details['group'])
            cur.execute("INSERT INTO purchase(id,location,date) VALUES (%s,%s,%s)", 
                        (item_id,group_data['location'],group_data['date'],))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('describe_item',item=item_id))
    return render_template('items_purchased.html', form=form)

@app.route('/items/bought_bulk',methods=["POST","GET"])
def bought_items():
    locations = get_all_from_locations()
    groups = get_all_from_groups()

    form = PurchaseForm()
    form.location.choices = [(location['id'], location['long_name']) for location in locations]
    form.group.choices = [(group['id'], group['name']) for group in groups]
    if request.method == "POST":
        details = request.form
        if 'not_selling' in request.form:
            not_selling = 2
        else:
            not_selling = 0
        cur = mysql.connection.cursor()
        #cur.execute("INSERT INTO items(name, group_id, sold) VALUES (%s, %s, %s)", 
                    (details['name'],details['group'],not_selling,))
        #mysql.connection.commit()
        #item_id = str(cur.lastrowid)
        #if details['group'] == "1":
        #    cur.execute("INSERT INTO purchase(id, location, date, price) VALUES (%s, %s, %s, %s)", 
        #                (item_id, details['location'], details['date'], details['price'],))
        #else:
        #    group_data = get_all_from_group(details['group'])
        #    cur.execute("INSERT INTO purchase(id,location,date) VALUES (%s,%s,%s)", 
        #                (item_id,group_data['location'],group_data['date'],))
        #mysql.connection.commit()
        cur.close()
        return redirect(url_for('describe_group',group_id=group_id))
    return render_template('items_purchased_bulk.html', form=form)

@app.route('/items/sold',methods=["POST","GET"])
def sold_items():
    locations = get_all_from_locations()
    items = get_all_items_not_sold()

    form = SaleForm()
    form.name.choices = [(item['id'], item['name']) for item in items]
    form.location.choices = [(location['id'], location['long_name']) for location in locations]
    if request.method == "POST":
        details = request.form
        if 'ebay' in request.form:
            ebay_fee = format(float(details['price']) * float(details['ebay_percent']), '.2f')
        else:
            ebay_fee = 0
       
        if details['paypal'] == "1":
            paypal_fee = format(((float(details['price']) + float(details['tax'])) * .029) + .3, '.2f')
        elif details['paypal'] == "2":
            paypal_fee = format(((float(details['price']) + float(details['tax'])) * .029), '.2f')
        else:
            paypal_fee = 0

        cur = mysql.connection.cursor()
        cur.execute("UPDATE items SET sold = 1 WHERE id = %s", (details['name'], ))
        cur.execute("""INSERT INTO sale(
                    id, 
                    location, 
                    date, 
                    price, 
                    tax, 
                    ebay_fee, 
                    paypal_fee, 
                    shipping_fee) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", 
                    (details['name'], details['location'], details['date'], details['price'],details['tax'], ebay_fee, paypal_fee, details['shipping_fee'], ))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('describe_item',item=details['name']))
    return render_template('items_sold.html', form=form)

#List Section
@app.route('/groups/list')
def groups_list():
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    groups.name, 
                    groups.price, 
                    groups.id,
                    groups.date,
                    sum(sale.price - sale.ebay_fee - sale.paypal_fee - sale.shipping_fee) AS net, 
                    location.long_name AS location 
                    FROM groups groups
                    LEFT JOIN location location ON groups.location = location.id
                    RIGHT JOIN items items ON groups.id = items.group_id 
                    LEFT JOIN sale sale ON sale.id = items.id
                    GROUP by items.group_id
                    ORDER by groups.id""")
    groups = list(cur.fetchall())
    return render_template('groups_list.html', groups=groups)

@app.route('/items/sold_list')
def sold_list():
    items = get_list_of_items_purchased_by_date(sold=1)

    cur = mysql.connection.cursor()    
    cur.execute("""SELECT
                    sale.id,
                    sale.date,
                    (sale.price - sale.ebay_fee - sale.paypal_fee - sale.shipping_fee) AS net
                    FROM sale
                    INNER JOIN items items ON items.id = sale.id
                    WHERE items.sold = 1""")
    sold = list(cur.fetchall())
    return render_template('items_sold_list.html', items=items, sold=sold)

@app.route('/items/unsold_list')
def unsold_list():
    items = get_list_of_items_purchased_by_date(sold=0)

    return render_template('items_unsold_list.html', items=items)

@app.route('/items/kept_list')
def kept_list():
    items = get_list_of_items_purchased_by_date(sold=2)

    return render_template('items_unsold_list.html', items=items)

#Describe Section
@app.route('/items/describe')
def describe_item():
    id = request.args.get('item', type = str)
    item = get_data_for_item_describe(id)
    if int(item[0]['sold']) == 1:
        item_sold = get_data_for_item_sold(id)
        sold_state = 1
    else:
        item_sold = 0
        sold_state = 0
    return render_template('items_describe.html', 
                            item=item,
                            sold=item_sold,
                            sold_state=sold_state)

@app.route('/groups/describe')
def describe_group():
    id = request.args.get('group_id', type = str)
    group_id = get_data_from_group_describe(id)
    items = get_data_from_item_groups(id)
    sold_price = get_group_profit(id)
    if not sold_price:
        sold_price = 0

    return render_template('groups_describe.html', 
                            group_id=group_id,
                            items=items,
                            sold_price=sold_price)

if __name__ == '__main__':
    app.run(debug=True)