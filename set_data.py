from flask import Flask
from flask_mysqldb import MySQL
from datetime import datetime, date, timedelta

import get_data

#Mysql Config
app = Flask(__name__)

mysql = MySQL(app)

#Item Data

def set_mark_sold(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE items SET sold = 1 where id = %s", (id,))
    mysql.connection.commit()
    cur.close()

def set_bought_items(details):
    cur = mysql.connection.cursor()
    for item in details:
        if item.startswith("item"):
            cur.execute("INSERT INTO items(name, group_id, category_id) VALUES (%s, %s, %s)", 
                        (details[item],details['group'],details['category'],))
            mysql.connection.commit()
            item_id = str(cur.lastrowid)
            cur.execute("INSERT INTO sale(id, price, shipping_fee, date) VALUES (%s, 0, 0, %s)",
                        (item_id,date.today().strftime("%Y-%m-%d"),))
            mysql.connection.commit()
    cur.close()

def set_quick_sale(details):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO items(name, group_id, category_id, sold) VALUES (%s, %s, %s, 1)", 
                (details['name'],details['group'],details['category'],))
    mysql.connection.commit()
    item_id = str(cur.lastrowid)
    cur.execute("INSERT INTO sale(id, price, shipping_fee, date) VALUES (%s, %s, %s, %s)",
                (item_id,details['price'],details['shipping_fee'],date.today().strftime("%Y-%m-%d"),))
    mysql.connection.commit()
    cur.close()
    return item_id

def set_sale_data(details):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE sale SET date = %s, price = %s, shipping_fee = %s WHERE id = %s", 
                (details['date'], details['price'], details['shipping_fee'], details['id'],))
    mysql.connection.commit()
    cur.close()


def set_items_modify(details):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE items SET name = %s, group_id = %s, category_id = %s, returned = %s where id = %s", 
                (details['name'], details['group'], details['category'], details['returned'], details['id']))
    mysql.connection.commit()
    cur.close()

#Group Data

def set_group_add(group_name, details, image_id):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO collection(name, date, price,image) VALUES (%s, %s, %s, %s)", 
                (group_name, details['date'], details['price'], image_id))
    mysql.connection.commit()
    group_id = str(cur.lastrowid)
    #cur.execute("INSERT INTO location(group_id, longitude, latitude) VALUES (%s, %s, %s)", 
    #            (group_id, details['longitude'], details['latitude']))
    mysql.connection.commit()
    cur.close()
    return group_id

def set_group_modify(details, image_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE collection SET name = %s, date = %s, price = %s, image = %s where id = %s", 
                (details['name'], details['date'], details['price'], image_id, details['id']))
    #cur.execute("UPDATE location set longitude = %s, latitude =%s where group_id =%s", 
    #            (details['longitude'], details['latitude'], details['id']))
    mysql.connection.commit()
    cur.close()

#Expense Data
def set_expense_gas(name, details, image_id):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO expenses(name, date, milage, image, type) VALUES (%s, %s, %s, %s, %s)", 
                   (name, details['date'], details['milage'], image_id, 1))
    mysql.connection.commit()
    cur.close()

def set_expense_store(name, details, image_id):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO expenses(name, date, price, image, type) VALUES (%s, %s, %s, %s, %s)", 
                   (name, details['date'], details['price'], image_id, 3))
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
                (details['name'], details['date'], price, milage, details['expense_type'], image_id, details['id']))
    mysql.connection.commit()
    cur.close()

#Timer
def start_timer_packing(id, time):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO timer(id, start_time, type) VALUES (%s, %s, %s)", 
            (id, time, 'packing'))
    mysql.connection.commit()
    cur.close()

def start_timer_listing(id, time):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO timer(group_id, start_time, type) VALUES (%s, %s, %s)", 
            (id, time, 'listing'))
    mysql.connection.commit()
    cur.close()

def start_timer_saling(time):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO timer(start_time, type, active) VALUES (%s, %s, %s)", 
            (time, 'saling', 'TRUE'))
    mysql.connection.commit()
    cur.close()

def end_timer_packing(id, time):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE timer SET end_time = %s WHERE id = %s", 
                (time, id))
    mysql.connection.commit()
    cur.close()

def end_timer_listing(id, time):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE timer SET end_time = %s WHERE group_id = %s", 
                (time, id))
    mysql.connection.commit()
    cur.close()

def end_timer_saling(start_time, time):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE timer SET end_time = %s, active = 'FALSE' where type='saling' AND start_time = %s", 
                (time, start_time))
    mysql.connection.commit()
    cur.close()