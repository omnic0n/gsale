from flask import Flask, session
from flask_mysqldb import MySQL
from flask_session import Session
import datetime

#Mysql Config
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mysql = MySQL(app)

#Get Years
def get_years():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM years")
    return list(cur.fetchall())

#Group Data
def get_all_from_group(group_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM collection WHERE id = %s", (group_id,))
    return cur.fetchone()

def get_all_from_group_and_items(date):
    if not date:
        date= '%' + str(datetime.date.today().year) + '%'
        print(date)
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
            collection.name, 
            collection.price, 
            collection.id,
            collection.date,
            sum(sale.price - sale.shipping_fee) AS net,
            COUNT(items.group_id) AS total_items 
            FROM collection collection
            RIGHT JOIN items items ON collection.id = items.group_id 
            LEFT JOIN sale sale ON sale.id = items.id
            WHERE collection.date LIKE %s AND collection.account = %s
            GROUP by items.group_id
            ORDER by collection.date""", (date, session['id'], ))
    return list(cur.fetchall())

def get_all_from_groups(date):
    cur = mysql.connection.cursor()
    if not date:
        date = str(datetime.date.today().year)
    cur.execute("SELECT * FROM collection WHERE date LIKE %s AND collection.account = %s ORDER BY name ASC", ('%' + date + '%', session['id'], ))
    return list(cur.fetchall())

def get_purchased_from_date(start_date, end_date):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT
                   date,
                   SUM(price) as price,
                   DAYNAME(date) as day
                   FROM collection
                   WHERE collection.date >= %s AND collection.date <= %s AND collection.account = %s GROUP by date ORDER BY date ASC""",
                   (start_date, end_date, session['id'], ))
    return list(cur.fetchall())

def get_purchased_from_day(day):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT
                   date,
                   SUM(price) as price,
                   DAYNAME(date) as day
                   FROM collection
                   WHERE DAYOFWEEK(collection.date) = %s AND collection.account = %s GROUP by date ORDER BY date ASC""",
                   (day, session['id'], ))
    return list(cur.fetchall())

def get_data_from_group_describe(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    collection.name, 
                    collection.price, 
                    collection.id,
                    collection.date,
                    collection.image
                    FROM collection collection
                    WHERE collection.id = %s""", (group_id, ))
    return list(cur.fetchall())

def get_group_sold_from_date(start_date, end_date):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT 
				    collection.date,
                    SUM(sale.price - sale.shipping_fee) AS net
                    FROM items items 
                    INNER JOIN sale sale ON items.id = sale.id
                    INNER JOIN collection collection ON items.group_id = collection.id
                    WHERE collection.date >= %s AND collection.date <= %s AND collection.account = %s GROUP BY collection.date""",
                    (start_date, end_date, session['id'], ))
    return list(cur.fetchall())

#Item Data
def get_group_id(item_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT group_id FROM items WHERE id = %s", (item_id, ))
    return cur.fetchone()

def get_all_from_items(item_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items WHERE id = %s", (item_id, ))
    return list(cur.fetchall())

def get_list_of_items_with_name(name):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT 
                items.name,
                items.sold,
                items.id,
                items.storage,
                collection.id as group_id,
                collection.name as group_name
                FROM items items 
                INNER JOIN collection collection ON items.group_id = collection.id
                WHERE items.name like %s AND collection.account = %s""", ('%'+ name + '%', session['id'], ))
    return list(cur.fetchall())

def get_data_from_item_groups(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    items.name, 
                    items.sold, 
                    items.id,
                    items.storage,
                    sum(sale.price - sale.shipping_fee) AS net 
                    FROM items items
                    INNER JOIN collection collection ON items.group_id = collection.id
                    LEFT JOIN sale sale ON sale.id = items.id
                    WHERE items.group_id = %s
                    GROUP BY items.id""", (group_id, ))
    return list(cur.fetchall())

def get_total_items_in_group(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT count(*) as total from items WHERE group_id = %s""", (group_id, ))
    return cur.fetchone()

def get_sold_from_date(start_date, end_date):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT 
				    sale.date,
                    SUM(sale.price) as price,
                    SUM(sale.shipping_fee) as shipping_fee,
                    SUM(sale.price - sale.shipping_fee) AS net,
                    COUNT(items.id) AS total_items,
                    DAYNAME(sale.date) AS day
                    FROM items items 
                    INNER JOIN collection collection ON collection.id = items.group_id
                    INNER JOIN sale sale ON items.id = sale.id
                    WHERE sale.date >= %s AND sale.date <= %s AND collection.account = %s GROUP BY sale.date ORDER BY sale.date ASC""",
                    (start_date, end_date, session['id'], ))
    return list(cur.fetchall())


def get_sold_from_day(day):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT 
				    sale.date,
                    SUM(sale.price) as price,
                    SUM(sale.shipping_fee) as shipping_fee,
                    SUM(sale.price - sale.shipping_fee) AS net,
                    COUNT(items.id) AS total_items,
                    DAYNAME(sale.date) AS day
                    FROM items items 
                    INNER JOIN collection collection ON collection.id = items.group_id
                    INNER JOIN sale sale ON items.id = sale.id
                    WHERE DAYOFWEEK(sale.date) = %s AND collection.account = %s GROUP BY sale.date ORDER BY sale.date ASC""",
                    (day, session['id'], ))
    return list(cur.fetchall())

def get_data_for_item_describe(item_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    items.name, 
                    items.sold, 
                    items.id,
                    items.group_id,
                    items.category_id,
                    items.returned,
                    items.storage,
                    collection.name AS group_name,
                    collection.date AS purchase_date
                    FROM items items
                    INNER JOIN collection collection ON items.group_id = collection.id
                    WHERE items.id = %s""", (item_id, ))
    return list(cur.fetchall())

def get_all_items_not_sold():
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT 
                * FROM items items 
                INNER JOIN collection collection ON items.group_id = collection.id  
                WHERE items.sold = 0 AND collection.account = %s ORDER BY items.name ASC""", (session['id'], ))
    return list(cur.fetchall())

def get_all_items_sold():
    cur = mysql.connection.cursor()    
    cur.execute("""SELECT
                    sale.id,
                    sale.date,
                    (sale.price - sale.shipping_fee) AS net
                    FROM sale
                    INNER JOIN items items ON items.id = sale.id
                    INNER JOIN collection collection ON items.group_id = collection.id 
                    WHERE items.sold = 1 AND collection.account = %s ORDER BY sale.date ASC""", (session['id'], ))
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
        if not date:
            date="%"
        cur = mysql.connection.cursor()
        cur.execute("""SELECT 
                    items.id, 
                    items.name, 
                    items.sold,
                    items.group_id,
                    items.storage,
                    sale.date as sales_date,
                    collection.date,
                    collection.name as group_name
                    FROM items items 
                    INNER JOIN collection collection ON items.group_id = collection.id
                    INNER JOIN sale sale on items.id = sale.id
                    WHERE sale.date LIKE %s AND sold = %s AND collection.account = %s""", (date, sold, session['id'], ))
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
                    collection.date
                    FROM items items 
                    INNER JOIN collection collection ON items.group_id = collection.id
                    INNER JOIN sale sale ON items.id = sale.id
                    INNER JOIN categories categories ON items.category_id = categories.id
                    WHERE categories.id = %s AND collection.account = %s
                    ORDER BY categories.id""",
                    (category_id, session['id'], ))
        return list(cur.fetchall())

#Expense Data
def get_expenses_choices():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM expenses_choices")
    return list(cur.fetchall())

def get_expenses_from_date(start_date, end_date, type):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT 
				    * FROM expenses
                    WHERE date >= %s AND date <= %s
                    AND type = %s
                    AND expenses.account = %s
					ORDER BY date""",
                    (start_date, end_date, type, session['id'], ))
    return list(cur.fetchall())

def get_all_from_expenses_date(start_date, end_date):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT 
				    * FROM expenses
                    WHERE date >= %s AND date <= %s
                    AND expenses.account = %s
					ORDER BY date""",
                    (start_date, end_date, session['id'], ))
    return list(cur.fetchall())

def get_all_from_expenses(date):
    cur = mysql.connection.cursor()
    if not date:
        cur.execute("SELECT * FROM expenses WHERE expenses.account = %s ORDER BY name ASC", (session['id'], ))
    else:
        cur.execute("SELECT * FROM expenses WHERE date LIKE %s AND expenses.account = %s ORDER BY name ASC", (date, session['id'], ))
    return list(cur.fetchall())

def get_data_for_expense_describe(id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    * FROM expenses
                    WHERE id = %s""", (id, ))
    return list(cur.fetchall())

#Category Data
def get_all_from_categories():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categories")
    return list(cur.fetchall())

def get_category(category_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT type FROM categories where id = %s", (category_id, ))
    return cur.fetchone()

#Profit Data
def get_profit(year):
    year_value = year + '-%-%'
    cur = mysql.connection.cursor()
    cur.execute("""SELECT SUM(tbl.price) AS price
                FROM (SELECT price FROM collection 
                      WHERE collection.account = %s 
                      AND collection.date LIKE %s) tbl""", (session['id'], year_value, ))
    purchase = list(cur.fetchall())
    if purchase[0]['price'] is None:
        purchase[0]['price'] = 0
    cur.execute("""SELECT 
                    sum((sale.price - sale.shipping_fee)) AS price 
                    FROM 
                    sale sale
                    INNER JOIN items items ON items.id = sale.id
                    INNER JOIN collection collection ON collection.id = items.group_id
                    WHERE collection.account = %s
                    AND collection.date LIKE %s""",(session['id'], year_value,  ))
    sale = list(cur.fetchall())
    if sale[0]['price'] is None:
        sale[0]['price'] = 0
    items = [sale[0]['price'],purchase[0]['price'],year]
    return items

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

#Location Data
def get_location(group_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT longitude, latitude FROM location WHERE group_id = %s", (group_id, ))
    return cur.fetchone()

def get_location_from_date(start_date, end_date):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT
                   collection.id,
                   collection.name,
                   location.latitude,
                   location.longitude
                   FROM location
                   INNER join collection collection on location.group_id = collection.id
                   WHERE collection.date >= %s AND collection.date <= %s
                   AND latitude != '' AND longitude != '' """,
                   (start_date, end_date,))
    return list(cur.fetchall())

#Platform Data
def get_all_from_platforms():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM platform")
    return list(cur.fetchall())

#Cases
def get_all_from_cases(platform):
    if not platform:
        platform = '%%'

    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT 
                cases.name,
                cases.id,
                cases.platform as platform_id,
                platform.name as platform_name
                FROM cases
                INNER JOIN platform platform on cases.platform = platform.id 
                WHERE cases.account = %s 
                AND
                cases.platform LIKE %s
                ORDER BY name ASC""", (session['id'],platform, ))
    return list(cur.fetchall())

def get_data_for_case_describe(case_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    cases.id, 
                    cases.name,
                    platform.id as platform_id, 
                    platform.name as platform_name
                    from cases
                    INNER JOIN platform platform on cases.platform = platform.id 
                    WHERE cases.id = %s""", (case_id, ))
    return list(cur.fetchall())

def get_list_of_cases_with_name(name):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT 
                cases.name,
                cases.id,
                cases.platform as platform_id,
                platform.name as platform_name
                FROM cases
                INNER JOIN platform platform on cases.platform = platform.id 
                WHERE cases.name like %s 
                AND 
                cases.account = %s""", ('%'+ name + '%', session['id'], ))
    return list(cur.fetchall())