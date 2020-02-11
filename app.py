from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from forms import PurchaseForm

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

def get_all_from_purchases(item_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM purchase where id = %s", (item_id, ))
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

@app.route('/items/list')
def items_list():
    cur = mysql.connection.cursor()
    cur.execute("SELECT t1.name, t1.sold, t2.long_name FROM items t1 INNER JOIN platform t2 ON t1.platform = t2.id")
    items = list(cur.fetchall())
    print items
    return render_template('items_list.html', items=items)

@app.route('/items/describe')
def describe_item():
    id = request.args.get('item', type = str)
    purchase = get_all_from_purchases(id)
    item = get_all_from_items(id)
    location = get_long_name_location_from_id(purchase[0]['location'])
    return render_template('items_describe.html', 
                            item=item,
                            purchase=purchase, 
                            location=location)

if __name__ == '__main__':
    app.run(debug=True)