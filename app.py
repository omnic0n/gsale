from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
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

@app.route('/items')
def items():
    return render_template('items.html')

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
    if request.method == "POST":
        details = request.form
        groupName = '_'.join([details['date'], details['location'], details['items']])
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
    return render_template('groups.html')

@app.route('/groups/list')
def groups_list():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM groups ORDER BY id ASC")
    groups = list(cur.fetchall())
    value = ''
    for group in groups:
        value += "<TR><TD>%s</TD><TD>%s</TD></TR>" % (str(group['id']), str(group['name']))
    return "<TABLE border = '1'><TR><TH>ID</TH><TH>Name</TH></TR>" + value + "</TABLE><BR><A HREF='/'>Home</A>"

if __name__ == '__main__':
    app.run(debut=True)