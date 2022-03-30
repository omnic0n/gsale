from flask import Flask
from flask_mysqldb import MySQL

#Mysql Config
app = Flask(__name__)

mysql = MySQL(app)

#Group Data
def get_all_from_group(group_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM groups WHERE id = %s", (group_id,))
    return cur.fetchone()

def get_all_from_group_and_items(date):
    if not date:
        date="%"
    cur = mysql.connection.cursor()
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
    return list(cur.fetchall())

def get_all_from_groups(date):
    cur = mysql.connection.cursor()
    if not date:
        cur.execute("SELECT * FROM groups ORDER BY name ASC")
    else:
        cur.execute("SELECT * FROM groups WHERE date LIKE %s ORDER BY name ASC", (date, ))
    return list(cur.fetchall())

def get_max_group_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM groups ORDER BY id DESC LIMIT 0,1")
    return cur.fetchone()

def get_purchased_from_date(start_date, end_date):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT
                   date,
                   SUM(price) as price
                   FROM groups
                   WHERE groups.date >= %s AND groups.date <= %s GROUP by date""",
                   (start_date, end_date,))
    return list(cur.fetchall())

def get_data_from_group_describe(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    groups.name, 
                    groups.price, 
                    groups.id,
                    groups.date,
                    groups.image,
                    longitude,
                    latitude
                    FROM groups groups
                    INNER JOIN location location ON location.group_id = groups.id
                    WHERE groups.id = %s""", (group_id, ))
    return list(cur.fetchall())

def get_group_sold_from_date(start_date, end_date):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT 
				    groups.date,
                    SUM(sale.price - sale.shipping_fee) AS net
                    FROM items items 
                    INNER JOIN sale sale ON items.id = sale.id
                    INNER JOIN groups groups ON items.group_id = groups.id
                    WHERE groups.date >= %s AND groups.date <= %s GROUP BY groups.date""",
                    (start_date, end_date,))
    return list(cur.fetchall())

#Item Data
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

def get_sold_from_date(start_date, end_date):
    print(start_date)
    print(end_date)
    cur = mysql.connection.cursor()
    cur.execute("""SELECT 
				    sale.date,
                    SUM(sale.price) as price,
                    SUM(sale.shipping_fee) as shipping_fee,
                    SUM(sale.price - sale.shipping_fee) AS net
                    FROM items items 
                    INNER JOIN sale sale ON items.id = sale.id
                    WHERE sale.date >= %s AND sale.date <= %s GROUP BY sale.date""",
                    (start_date, end_date,))
    return list(cur.fetchall())

def get_max_item_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM items ORDER BY id DESC LIMIT 0,1")
    return cur.fetchone()

def get_data_for_item_describe(item_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    items.name, 
                    items.sold, 
                    items.id,
                    items.group_id,
                    items.category_id,
                    groups.name AS group_name,
                    groups.date AS purchase_date
                    FROM items items
                    INNER JOIN groups groups ON items.group_id = groups.id
                    WHERE items.id = %s""", (item_id, ))
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
                    sale.date as sales_date,
                    groups.date
                    FROM items items 
                    INNER JOIN groups groups ON items.group_id = groups.id
                    INNER JOIN sale sale on items.id = sale.id
                    WHERE sale.date LIKE %s AND sold = %s""", (date, sold, ))
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
                    groups.date
                    FROM items items 
                    INNER JOIN groups groups ON items.group_id = groups.id
                    INNER JOIN sale sale ON items.id = sale.id
                    INNER JOIN categories categories ON items.category_id = categories.id
                    WHERE categories.id = %s
                    ORDER BY categories.id""",
                    (category_id,))
        return list(cur.fetchall())

#Expense Data
def get_expenses_from_date(start_date, end_date, type):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT 
				    * FROM expenses
                    WHERE date >= %s AND date <= %s
                    AND type = %s
					ORDER BY date""",
                    (start_date, end_date, type,))
    return list(cur.fetchall())

def get_all_from_expenses(date):
    cur = mysql.connection.cursor()
    if not date:
        cur.execute("SELECT * FROM expenses ORDER BY name ASC")
    else:
        cur.execute("SELECT * FROM expenses WHERE date LIKE %s ORDER BY name ASC", (date, ))
    return list(cur.fetchall())

def get_data_for_expense_describe(id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    * FROM expenses
                    WHERE id = %s""", (id, ))
    return list(cur.fetchall())

def get_max_expense_id():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM expenses ORDER BY id DESC LIMIT 0,1")
    return cur.fetchone()

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

#Location Data
def get_location(group_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT longitude, latitude FROM location WHERE group_id = %s", (group_id, ))
    return cur.fetchone()

def get_location_from_date(start_date, end_date):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT
                   groups.id,
                   groups.name,
                   location.latitude,
                   location.longitude
                   FROM location
                   INNER join groups groups on location.group_id = groups.id
                   WHERE groups.date >= %s AND groups.date <= %s
                   AND latitude != '' AND longitude != '' """,
                   (start_date, end_date,))
    return list(cur.fetchall())

#Timer Data
def get_timer_data_for_item(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM timer WHERE id = %s", (id, ))
    return cur.fetchone()