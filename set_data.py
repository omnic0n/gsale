from flask import Flask, session
from flask_mysqldb import MySQL
from flask_session import Session
from datetime import datetime, date, timedelta

import uuid

import get_data

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mysql = MySQL(app)

#Item Data

def generate_uuid():
    return uuid.uuid4()

def set_mark_sold(id,sold):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE items SET sold = %s where id = %s", (sold, id,))
    mysql.connection.commit()
    cur.close()

def set_bought_items(details, list_date):
    cur = mysql.connection.cursor()
    for item in details:
        if item.startswith("item"):
            item_id = generate_uuid()
            cur.execute("INSERT INTO items(id, name, group_id, category_id, storage, list_date) VALUES (%s, %s, %s, %s, %s, %s)", 
                        (item_id, details[item],details['group'],details['category'],details['storage'],))
            cur.execute("INSERT INTO sale(id, price, shipping_fee, date) VALUES (%s, 0, 0, %s)",
                        (item_id, date.today().strftime("%Y-%m-%d"),))
            mysql.connection.commit()
    cur.close()

def set_quick_sale(details, list_date):
    item_id = generate_uuid()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO items(id, name, group_id, category_id, list_date, sold) VALUES (%s, %s, %s, %s, %s, 1)", 
                (item_id, details['name'],details['group'],details['category'],))
    cur.execute("INSERT INTO sale(id, price, shipping_fee, date) VALUES (%s, %s, %s, %s)",
                (item_id,details['price'],details['shipping_fee'],date.today().strftime("%Y-%m-%d"),))
    mysql.connection.commit()
    cur.close()
    return item_id

def set_sale_data(details):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE sale SET date = %s, price = %s, shipping_fee = %s WHERE id = %s", 
                (details['sale_date'], details['price'], details['shipping_fee'], details['id'],))
    mysql.connection.commit()
    cur.close()


def set_items_modify(details):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE items SET name = %s, group_id = %s, category_id = %s, returned = %s, storage = %s, list_date = %s where id = %s", 
                (details['name'], details['group'], details['category'], details['returned'], details['storage'], details['list_date'], details['id']))
    mysql.connection.commit()
    cur.close()

def remove_item_data(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM items WHERE id = %s", 
                (id, ))
    mysql.connection.commit()
    cur.close()

#Group Data

def set_group_add(group_name, details, image_id):
    group_id = generate_uuid()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO collection(id, name, date, price, image, account) VALUES (%s, %s, %s, %s, %s, %s)", 
                (group_id, group_name, details['date'], details['price'], image_id, session['id']))
    mysql.connection.commit()
    cur.close()
    return group_id

def set_group_modify(details, image_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE collection SET name = %s, date = %s, price = %s, image = %s where id = %s", 
                (details['name'], details['date'], details['price'], image_id, details['id']))
    mysql.connection.commit()
    cur.close()

#Expense Data
def set_expense(name, details, image_id, expense_type):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO expenses(name, date, price, image, type, account) VALUES (%s, %s, %s, %s, %s, %s)", 
                (name, details['date'], details['price'], image_id, expense_type, session['id']))
    mysql.connection.commit()
    cur.close()

def set_modify_expense(details, price, milage, image_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE expenses SET name = %s, date = %s, price = %s, milage = %s, type = %s, image = %s where id = %s", 
                (details['name'], details['date'], price, milage, details['expense_type'], image_id, details['id']))
    mysql.connection.commit()
    cur.close()

#Cases

def add_case_data(details):
    cur = mysql.connection.cursor()
    for item in details:
        if item.startswith("item"):
            item_id = generate_uuid()
            cur.execute("INSERT INTO cases(id, name, platform,account) VALUES (%s, %s, %s, %s)", 
                        (item_id, details[item],details['platform'],session['id'],))
            mysql.connection.commit()
    cur.close()

def set_cases_modify(details):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE cases SET name = %s, platform = %s where id = %s", 
                (details['name'], details['platform'], details['id']))
    mysql.connection.commit()
    cur.close()


def remove_case_data(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cases WHERE id = %s", 
                (id, ))
    mysql.connection.commit()
    cur.close()