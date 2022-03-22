from flask import Flask
from flask_mysqldb import MySQL

#Mysql Config
app = Flask(__name__)

app.secret_key = '4T3*%go^Gcn7TrYm'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'gsale'
app.config['MYSQL_PASSWORD'] = 'DR1wZcjTF7858gnu'
app.config['MYSQL_DB'] = 'gsale'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

mysql = MySQL(app)

#Group Data
def set_group_add(group_name, details, image_id):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO groups(name, date, price,image) VALUES (%s, %s, %s, %s)", 
                (group_name, details['date'], details['price'], image_id))
    mysql.connection.commit()
    group_id = str(cur.lastrowid)
    cur.execute("INSERT INTO location(group_id, longitude, latitude) VALUES (%s, %s, %s)", 
                (group_id, details['longitude'], details['latitude']))
    mysql.connection.commit()
    cur.close()
    return group_id

def set_group_modify(details, image_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE groups SET name = %s, date = %s, price = %s, image = %s where id = %s", 
                (details['name'], details['date'], details['price'], image_id, details['id']))
    cur.execute("UPDATE location set longitude = %s, latitude =%s where group_id =%s", 
    (details['longitude'], details['latitude'], details['id']))
    mysql.connection.commit()
    cur.close()

#Expense Data
def set_expense_gas(name, details, image_id):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO expenses(name, date, milage, image, type) VALUES (%s, %s, %s, %s, %s)", 
                   (name, details['date'], details['milage'], image_id, 1))
    mysql.connection.commit()
    cur.close()

def set_expense_item(name, details, image_id):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO expenses(name, date, price, image, type) VALUES (%s, %s, %s, %s, %s)", 
                (name, details['date'], details['price'], image_id, 2))
    mysql.connection.commit()
    cur.close()

def set_modify_expense(details, price, milage, image_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE expenses SET name = %s, date = %s, price = %s, milage = %s, type = %s, image = %s where id = %s", 
                (details['name'], details['date'], price, milage, details['type'], image_id, details['id']))
    mysql.connection.commit()
    cur.close()