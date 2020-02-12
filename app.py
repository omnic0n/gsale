from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from forms import PurchaseForm, SaleForm

app = Flask(__name__)

app.secret_key = '4T3*%go^Gcn7TrYm'

app.config['MYSQL_HOST'] = 'gsale.cz541jbd6nid.us-east-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'gsale'
app.config['MYSQL_PASSWORD'] = 'DR1wZcjTF7858gnu'
app.config['MYSQL_DB'] = 'gsale'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def get_long_name_location_from_id(location_id):
    cur = mysql.connection.cursor()
    value = cur.execute("SELECT long_name FROM location where id = %s", (location_id,))
    return cur.fetchone()['long_name']

def get_all_from_items(item_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items where id = %s", (item_id, ))
    return list(cur.fetchall())

def get_all_items_not_sold():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items where sold = 0")
    return list(cur.fetchall())

def get_data_for_item_describe(item_id):
    cur = mysql.connection.cursor()
    cur.execute(""" select 
                    items.name, 
                    items.sold, 
                    items.id, 
                    platform.long_name as platform, 
                    purchase.price, 
                    purchase.date, 
                    location.long_name as location 
                    from items items
                    inner join platform platform on items.platform = platform.id 
                    inner join purchase purchase on purchase.id = items.id
                    inner join location location on purchase.location = location.id
                    where items.id = %s""", (item_id, ))
    return list(cur.fetchall())

def get_data_for_item_sold(item_id):
    cur = mysql.connection.cursor()
    cur.execute(""" select 
                    sale.price, 
                    sale.tax,
                    sale.date, 
                    sale.ebay_fee,
                    sale.paypal_fee,
                    sale.shipping_fee,
                    (sale.price - sale.ebay_fee - sale.paypal_fee - sale.shipping_fee) as net,
                    location.long_name as location 
                    from sale sale
                    inner join location location on sale.location = location.id
                    where sale.id = %s""", (item_id, ))
    return list(cur.fetchall())

def get_all_from_locations():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM location ORDER BY name ASC")
    return list(cur.fetchall())

def get_all_from_platforms():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM platform ORDER BY name ASC")
    return list(cur.fetchall())

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    purchase = cur.execute("select sum(price) as total from purchase")
    purchase = list(cur.fetchall())
    print purchase['total']
    return render_template('index.html')

@app.route('/items/bought',methods=["POST","GET"])
def bought_items():
    locations = get_all_from_locations()
    platforms = get_all_from_platforms()

    form = PurchaseForm()
    form.location.choices = [(location['id'], location['long_name']) for location in locations]
    form.platform.choices = [(platform['id'], platform['long_name']) for platform in platforms]
    if request.method == "POST":
        details = request.form
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO items(name, platform) VALUES (%s, %s)", 
                    (details['name'], details['platform']))
        mysql.connection.commit()
        cur.execute("INSERT INTO purchase(id, location, date, price) VALUES (%s, %s, %s, %s)", 
                    (str(cur.lastrowid), details['location'], details['date'], details['price'],))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('bought_items'))
    return render_template('items_purchased.html', form=form)

@app.route('/items/sold',methods=["POST","GET"])
def sold_items():
    locations = get_all_from_locations()
    items = get_all_items_not_sold()

    form = SaleForm()
    form.name.choices = [(item['id'], item['name']) for item in items]
    form.location.choices = [(location['id'], location['long_name']) for location in locations]
    if request.method == "POST":
        details = request.form
        cur = mysql.connection.cursor()
        if details['ebay']:
            ebay_fee = format(float(details['price']) * .10, '.2f')
        else:
            ebay_fee = 0

        if details['paypal']:
            paypal_fee = format(((float(details['price']) + float(details['tax'])) * .029) + .3, '.2f')
        else:
            paypal_fee = 0
        
        cur.execute("update items set sold = 1 where id = %s", (details['name'], ))
        mysql.connection.commit()
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
        return redirect(url_for('sold_items'))
    return render_template('items_sold.html', form=form)

@app.route('/items/list')
def items_list():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT 
                 t1.id, 
                 t1.name, 
                 t1.sold, 
                 t2.long_name as platform 
                 FROM items t1 
                 INNER JOIN platform t2 
                 ON t1.platform = t2.id""")
    items = list(cur.fetchall())
    return render_template('items_list.html', items=items)

@app.route('/items/describe')
def describe_item():
    id = request.args.get('item', type = str)
    item = get_data_for_item_describe(id)
    if int(item[0]['sold']) == 1:
        sold = get_data_for_item_sold(id)
        return render_template('items_describe_with_sold.html', 
                                item=item,
                                sold=sold)
    else:
        return render_template('items_describe.html', 
                                item=item)


if __name__ == '__main__':
    app.run(debug=True)