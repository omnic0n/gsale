from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from forms import PurchaseForm, AddGroup

app = Flask(__name__)

app.secret_key = '4T3*%go^Gcn7TrYm'

app.config['MYSQL_HOST'] = 'gsale.cz541jbd6nid.us-east-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'gsale'
app.config['MYSQL_PASSWORD'] = 'DR1wZcjTF7858gnu'
app.config['MYSQL_DB'] = 'gsale'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/items/bought',methods=["POST","GET"])
def bought_items():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,name FROM groups ORDER BY id ASC")
    groups = list(cur.fetchall())
    cur.execute("SELECT * FROM location ORDER BY id ASC")
    locations = list(cur.fetchall())

    form = PurchaseForm()
    form.group.choices = [(group['id'], group['name']) for group in groups]
    form.location.choices = [(location['id'], location['long_name']) for location in locations]
    if request.method == "POST":
        details = request.form
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO items(group_id, name, description) VALUES (%s, %s, %s)", 
                    (details['group'], details['name'], details['description']))
        mysql.connection.commit()
        cur.execute("INSERT INTO purchase(id, location, date, price) VALUES (%s, %s, %s, %s)", 
                    (str(cur.lastrowid), details['location'], details['date'], details['price'],))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('bought_items'))
    return render_template('items_purchased.html', form=form)

@app.route("/livesearch",methods=["POST","GET"])
def livesearch():
    searchbox = request.form.get("text")
    cur = mysql.connection.cursor()
    query = "select * from groups where name LIKE '%{}%' order by name".format(searchbox)
    cur.execute(query)
    result = list(cur.fetchall())
    return jsonify(result)

@app.route('/groups/add', methods=['GET', 'POST'])
def groups_add():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM location ORDER BY id ASC")
    locations = list(cur.fetchall())

    form = AddGroup()
    form.location.choices = [(location['id'], location['long_name']) for location in locations]
    if not form.validate_on_submit():
        return render_template('groups_add.html',form=form)
    if request.method == "POST":
        details = request.form
        cur.execute("SELECT name FROM location where id = %s", details['location'])
        location = cur.fetchone()['name']
        groupName = '_'.join([details['date'], location, details['name']])
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM groups where name = %s", (groupName,))
        rv = cur.fetchone()
        if not cur.rowcount:
            cur.execute("INSERT INTO groups(name) VALUES (%s)", (groupName,))
            mysql.connection.commit()
            flash('Successfully added value to groups')
        else:
            flash('This value already exists')
        cur.close()
        return redirect(url_for('groups_add'))
    return render_template('groups_add.html', form=form)

@app.route('/groups/list')
def groups_list():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM groups ORDER BY id ASC")
    groups = list(cur.fetchall())
    return render_template('groups_list.html', groups=groups)

@app.route('/items/list')
def items_list():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items ORDER BY id ASC")
    items = list(cur.fetchall())
    return render_template('items_list.html', items=items)

@app.route('/items/describe')
def describe_item():
    id = request.args.get('item', type = str)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items where id = %s", (id, ))
    item = list(cur.fetchall())
    cur.execute("SELECT * FROM purchase where id = %s", (id, ))
    purchase = list(cur.fetchall())
    cur.execute("SELECT long_name FROM location where id = %s", (purchase[0]['location'],))
    location = cur.fetchone()['name']
    return render_template('items_describe.html', item=item, purchase=purchase, location=location)

if __name__ == '__main__':
    app.run(debug=True)