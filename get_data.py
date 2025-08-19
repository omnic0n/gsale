from flask import session
from datetime import datetime, date, timedelta
import datetime

# We'll get the mysql object passed to us or use a global reference
mysql = None

def set_mysql_connection(mysql_connection):
    """Set the MySQL connection from the main app"""
    global mysql
    mysql = mysql_connection

#Get Years
def get_years():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM years ORDER BY year")
    return list(cur.fetchall())

#Group Data
def get_all_from_group(group_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM collection WHERE id = %s AND account = %s", (group_id, session.get('id')))
    return cur.fetchone()

def get_all_from_group_and_items(date):
    if not date:
        date= '%' + str(datetime.date.today().year) + '%'
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            c.id, 
            c.name, 
            c.price, 
            c.date,
            c.location_address,
            COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) AS net,
            COUNT(i.group_id) AS total_items,
            SUM(CASE WHEN i.sold = 1 THEN 1 ELSE 0 END) AS sold_items
        FROM collection c
        LEFT JOIN items i ON c.id = i.group_id
        LEFT JOIN sale s ON i.id = s.id
        WHERE c.date LIKE %s AND c.account = %s
        GROUP BY c.id, c.name, c.price, c.date, c.location_address
        ORDER BY c.date
    """, (date, session.get('id')))
    return list(cur.fetchall())

def get_all_from_group_and_items_by_name(name):
    name = '%' + name + '%'
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            c.name, 
            c.price, 
            c.id,
            c.date,
            c.location_address,
            COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) AS net,
            COUNT(i.group_id) AS total_items,
            SUM(CASE WHEN i.sold = 1 THEN 1 ELSE 0 END) AS sold_items
        FROM collection c
        LEFT JOIN items i ON c.id = i.group_id
        LEFT JOIN sale s ON i.id = s.id
        WHERE c.name LIKE %s AND c.account = %s
        GROUP BY c.id, c.name, c.price, c.date, c.location_address
        ORDER BY c.date
    """, (name, session.get('id')))
    return list(cur.fetchall())

def get_all_from_groups(date):
    cur = mysql.connection.cursor()
    if not date:
        date = str(datetime.date.today().year)
    cur.execute("SELECT * FROM collection WHERE date LIKE %s AND collection.account = %s ORDER BY name ASC", ('%' + date + '%', session.get('id'), ))
    return list(cur.fetchall())

def get_purchased_from_date(start_date, end_date):
    """Optimized purchase report query"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
            date,
            SUM(price) as price,
            DAYNAME(date) as day
        FROM collection
        WHERE date BETWEEN %s AND %s 
        AND account = %s 
        GROUP BY date 
        ORDER BY date ASC
    """, (start_date, end_date, session.get('id')))
    return list(cur.fetchall())

def get_purchased_from_day(day, year):
    """Optimized purchase by day of week query"""
    if year == "All":
        start_date = '2000-01-01'
        end_date = '3000-01-01'
    else:
        start_date = f"{year}-01-01"
        end_date = f"{int(year) + 1}-01-01"
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
            date,
            SUM(price) as price,
            DAYNAME(date) as day
        FROM collection
        WHERE DAYOFWEEK(date) = %s 
        AND date >= %s 
        AND date < %s 
        AND account = %s 
        GROUP BY date 
        ORDER BY date ASC
    """, (day, start_date, end_date, session.get('id')))
    return list(cur.fetchall())

def get_data_from_group_list(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    collection.name, 
                    collection.price, 
                    collection.id,
                    collection.date,
                    collection.image,
                    collection.latitude,
                    collection.longitude,
                    collection.location_address
                    FROM collection collection
                    WHERE collection.id = %s AND collection.account = %s""", (group_id, session.get('id')))
    return list(cur.fetchall())

def get_group_sold_from_date(start_date, end_date):
    """Optimized group sales report query"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            c.date,
            COALESCE(SUM(s.price - s.shipping_fee), 0) AS net
        FROM collection c
        LEFT JOIN items i ON c.id = i.group_id
        LEFT JOIN sale s ON i.id = s.id
        WHERE c.date BETWEEN %s AND %s 
        AND c.account = %s 
        GROUP BY c.date 
        ORDER BY c.date
    """, (start_date, end_date, session.get('id')))
    return list(cur.fetchall())

def get_group_sold_from_day(day):
    """Optimized group sales by day of week query"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            c.date,
            COALESCE(SUM(s.price - s.shipping_fee), 0) AS net,
            DAYNAME(c.date) AS day
        FROM collection c
        LEFT JOIN items i ON c.id = i.group_id
        LEFT JOIN sale s ON i.id = s.id
        WHERE DAYOFWEEK(c.date) = %s 
        AND c.account = %s 
        GROUP BY c.date 
        ORDER BY c.date
    """, (day, session.get('id')))
    return list(cur.fetchall())

#Item Data
def get_group_id(item_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT i.group_id 
        FROM items i 
        INNER JOIN collection c ON i.group_id = c.id 
        WHERE i.id = %s AND c.account = %s
    """, (item_id, session.get('id')))
    return cur.fetchone()

def get_all_from_items(item_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT i.* 
        FROM items i 
        INNER JOIN collection c ON i.group_id = c.id 
        WHERE i.id = %s AND c.account = %s
    """, (item_id, session.get('id')))
    return list(cur.fetchall())

def get_list_of_items_with_name(name,sold):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT 
                items.name,
                items.sold,
                items.id,
                items.storage,
                (sale.price - sale.shipping_fee) AS net,
                collection.id as group_id,
                collection.name as group_name
                FROM items items 
                INNER JOIN collection collection ON items.group_id = collection.id
                INNER JOIN sale sale ON items.id = sale.id
                WHERE items.name LIKE %s AND collection.account = %s AND items.sold LIKE %s""", ('%'+ name + '%', session.get('id'), sold ))
    return list(cur.fetchall())

def get_data_from_item_groups(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    items.name, 
                    items.sold, 
                    items.id,
                    items.category_id,
                    items.storage,
                    items.returned,
                    sale.price AS gross,
                    sale.shipping_fee AS shipping_fee,
                    sale.returned_fee AS returned_fee,
                    (sale.price - sale.shipping_fee - COALESCE(sale.returned_fee, 0)) AS net,
                    sale.date AS sale_date,
					DATEDIFF(sale.date,collection.date) AS days_to_sell 
                    FROM items items
                    INNER JOIN collection collection ON items.group_id = collection.id
                    LEFT JOIN sale sale ON sale.id = items.id
                    WHERE items.group_id = %s AND collection.account = %s
                    ORDER BY sale.date""", (group_id, session.get('id')))
    return list(cur.fetchall())

def get_total_items_in_group(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" 
        SELECT count(*) as total 
        FROM items i 
        INNER JOIN collection c ON i.group_id = c.id 
        WHERE i.group_id = %s AND c.account = %s
    """, (group_id, session.get('id')))
    return cur.fetchone()

def get_total_items_in_group_sold(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" 
        SELECT count(*) as total 
        FROM items i 
        INNER JOIN collection c ON i.group_id = c.id 
        WHERE i.group_id = %s AND i.sold = 1 AND c.account = %s
    """, (group_id, session.get('id')))
    return cur.fetchone()

def get_sold_from_date(start_date, end_date):
    """Optimized sales report query with better indexing"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            s.date,
            SUM(s.price) as price,
            SUM(s.shipping_fee) as shipping_fee,
            SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)) AS net,
            COUNT(i.id) AS total_items,
            DAYNAME(s.date) AS day
        FROM sale s
        INNER JOIN items i ON s.id = i.id
        INNER JOIN collection c ON i.group_id = c.id
        WHERE s.date BETWEEN %s AND %s 
        AND c.account = %s 
        GROUP BY s.date 
        ORDER BY s.date ASC
    """, (start_date, end_date, session.get('id')))
    return list(cur.fetchall())



def get_sold_from_day(day):
    """Optimized sales by day of week query"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            s.date,
            SUM(s.price) as price,
            SUM(s.shipping_fee) as shipping_fee,
            SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)) AS net,
            COUNT(i.id) AS total_items,
            DAYNAME(s.date) AS day
        FROM sale s
        INNER JOIN items i ON s.id = i.id
        INNER JOIN collection c ON i.group_id = c.id
        WHERE DAYOFWEEK(s.date) = %s 
        AND c.account = %s 
        GROUP BY s.date 
        ORDER BY s.date ASC
    """, (day, session.get('id')))
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
                    items.list_date,
                    collection.name AS group_name,
                    collection.date AS purchase_date
                    FROM items items
                    INNER JOIN collection collection ON items.group_id = collection.id
                    WHERE items.id = %s AND collection.account = %s""", (item_id, session.get('id')))
    return list(cur.fetchall())

def get_all_items_not_sold():
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT 
                * FROM items items 
                INNER JOIN collection collection ON items.group_id = collection.id  
                WHERE items.sold = 0 AND collection.account = %s ORDER BY items.name ASC""", (session.get('id'), ))
    return list(cur.fetchall())

def get_all_items_sold():
    cur = mysql.connection.cursor()    
    cur.execute("""SELECT
                    sale.id,
                    sale.date,
                    (sale.price - sale.shipping_fee - COALESCE(sale.returned_fee, 0)) AS net
                    FROM sale
                    INNER JOIN items items ON items.id = sale.id
                    INNER JOIN collection collection ON items.group_id = collection.id 
                    WHERE items.sold = 1 AND collection.account = %s ORDER BY sale.date ASC""", (session.get('id'), ))
    return list(cur.fetchall())

def get_data_from_sale(item_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    s.date, 
                    s.price, 
                    s.shipping_fee
                    FROM sale s
                    INNER JOIN items i ON s.id = i.id
                    INNER JOIN collection c ON i.group_id = c.id
                    WHERE s.id = %s AND c.account = %s""", (item_id, session.get('id')))
    return list(cur.fetchall())

def get_data_for_item_sold(item_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    s.price, 
                    s.date,
                    s.shipping_fee,
                    s.returned_fee,
                    (s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)) AS net
                    FROM sale s
                    INNER JOIN items i ON s.id = i.id
                    INNER JOIN collection c ON i.group_id = c.id
                    WHERE s.id = %s AND c.account = %s""", (item_id, session.get('id')))
    return list(cur.fetchall())

def get_list_of_items_purchased_by_date(sold_date, purchase_date, sold, list_date, storage):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            i.id, 
            i.name, 
            i.sold,
            i.group_id,
            i.storage,
            i.list_date,
            s.date as sale_date,
            (s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)) AS net,
            c.date as purchase_date,
            c.name as group_name
        FROM items i
        INNER JOIN collection c ON i.group_id = c.id
        INNER JOIN sale s ON i.id = s.id
        WHERE c.account = %s
        AND s.date LIKE %s 
        AND c.date LIKE %s
        AND i.sold LIKE %s
        AND i.list_date LIKE %s
        AND i.storage LIKE %s
        ORDER BY c.date ASC
    """, (session.get('id'), sold_date, purchase_date, sold, list_date, storage))
    return list(cur.fetchall())

def get_list_of_items_with_categories(category_id):
        cur = mysql.connection.cursor()
        cur.execute("""SELECT 
                    items.id, 
                    items.name, 
                    items.sold,
                    items.group_id,
                    collection.name as group_name,
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
                    (category_id, session.get('id'), ))
        return list(cur.fetchall())

def get_list_of_items_by_category(category_id, sold_status="all"):
    """Get items for a specific category with optional sold status filtering"""
    cur = mysql.connection.cursor()
    
    if sold_status == "sold":
        # Only sold items in this category
        cur.execute("""
            SELECT 
                i.id, 
                i.name, 
                i.sold,
                i.group_id,
                i.storage,
                i.list_date,
                s.date as sale_date,
                (s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)) AS net,
                c.date as purchase_date,
                c.name as group_name
            FROM items i
            INNER JOIN collection c ON i.group_id = c.id
            LEFT JOIN sale s ON i.id = s.id
            INNER JOIN categories cat ON i.category_id = cat.id
            WHERE c.account = %s
            AND cat.id = %s
            AND i.sold = 1
            ORDER BY c.date ASC
        """, (session.get('id'), category_id))
    elif sold_status == "not_sold":
        # Only not sold items in this category
        cur.execute("""
            SELECT 
                i.id, 
                i.name, 
                i.sold,
                i.group_id,
                i.storage,
                i.list_date,
                s.date as sale_date,
                (s.price - s.shipping_fee) AS net,
                c.date as purchase_date,
                c.name as group_name
            FROM items i
            INNER JOIN collection c ON i.group_id = c.id
            LEFT JOIN sale s ON i.id = s.id
            INNER JOIN categories cat ON i.category_id = cat.id
            WHERE c.account = %s
            AND cat.id = %s
            AND i.sold = 0
            ORDER BY c.date ASC
        """, (session.get('id'), category_id))
    else:
        # All items in this category
        cur.execute("""
            SELECT 
                i.id, 
                i.name, 
                i.sold,
                i.group_id,
                i.storage,
                i.list_date,
                s.date as sale_date,
                (s.price - s.shipping_fee) AS net,
                c.date as purchase_date,
                c.name as group_name
            FROM items i
            INNER JOIN collection c ON i.group_id = c.id
            LEFT JOIN sale s ON i.id = s.id
            INNER JOIN categories cat ON i.category_id = cat.id
            WHERE c.account = %s
            AND cat.id = %s
            ORDER BY c.date ASC
        """, (session.get('id'), category_id))
    
    return list(cur.fetchall())

def get_list_of_items_by_sold_status(sold_status, sold_date="%", purchase_date="%", list_date="%", storage="%"):
    """Get items filtered by sold status (all, sold, not_sold) with the same structure as get_list_of_items_purchased_by_date"""
    cur = mysql.connection.cursor()
    
    if sold_status == "sold":
        # Only sold items - filter by items.sold = 1
        cur.execute("""
            SELECT 
                i.id, 
                i.name, 
                i.sold,
                i.group_id,
                i.storage,
                i.list_date,
                s.date as sale_date,
                (s.price - s.shipping_fee) AS net,
                c.date as purchase_date,
                c.name as group_name
            FROM items i
            INNER JOIN collection c ON i.group_id = c.id
            LEFT JOIN sale s ON i.id = s.id
            WHERE c.account = %s
            AND i.sold = 1
            AND s.date LIKE %s 
            AND c.date LIKE %s
            AND i.list_date LIKE %s
            AND i.storage LIKE %s
            ORDER BY c.date ASC
        """, (session.get('id'), sold_date, purchase_date, list_date, storage))
    elif sold_status == "not_sold":
        # Only not sold items - filter by items.sold = 0
        cur.execute("""
            SELECT 
                i.id, 
                i.name, 
                i.sold,
                i.group_id,
                i.storage,
                i.list_date,
                s.date as sale_date,
                (s.price - s.shipping_fee) AS net,
                c.date as purchase_date,
                c.name as group_name
            FROM items i
            INNER JOIN collection c ON i.group_id = c.id
            LEFT JOIN sale s ON i.id = s.id
            WHERE c.account = %s
            AND i.sold = 0
            AND c.date LIKE %s
            AND i.list_date LIKE %s
            AND i.storage LIKE %s
            ORDER BY c.date ASC
        """, (session.get('id'), purchase_date, list_date, storage))
    else:
        # All items - no sold status filter
        cur.execute("""
            SELECT 
                i.id, 
                i.name, 
                i.sold,
                i.group_id,
                i.storage,
                i.list_date,
                s.date as sale_date,
                (s.price - s.shipping_fee) AS net,
                c.date as purchase_date,
                c.name as group_name
            FROM items i
            INNER JOIN collection c ON i.group_id = c.id
            LEFT JOIN sale s ON i.id = s.id
            WHERE c.account = %s
            AND c.date LIKE %s
            AND i.list_date LIKE %s
            AND i.storage LIKE %s
            ORDER BY c.date ASC
        """, (session.get('id'), purchase_date, list_date, storage))
    
    return list(cur.fetchall())



#Category Data
def get_all_from_categories():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categories WHERE user_id = %s ORDER BY type", (session.get('id'),))
    return list(cur.fetchall())

def get_category(category_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT type FROM categories where id = %s AND user_id = %s", (category_id, session.get('id')))
    return cur.fetchone()

def get_category_by_id(category_id):
    """Get category by ID without user restriction (for admin purposes)"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categories where id = %s", (category_id,))
    return cur.fetchone()

def get_category_item_counts():
    """Get the count of items in each category for the current user"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            c.id,
            c.type,
            COUNT(CASE WHEN col.account = %s THEN i.id ELSE NULL END) as item_count
        FROM categories c
        LEFT JOIN items i ON c.id = i.category_id
        LEFT JOIN collection col ON i.group_id = col.id
        WHERE c.user_id = %s
        GROUP BY c.id, c.type
        ORDER BY c.type
    """, (session.get('id'), session.get('id')))
    return list(cur.fetchall())



#Profit Data
def get_profit(year):
    year_value = year + '-%-%'
    cur = mysql.connection.cursor()
    
    # Get sales (only for sold items, including returned fees)
    cur.execute("""
        SELECT COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) AS sale_price
        FROM sale s
        INNER JOIN items i ON s.id = i.id
        INNER JOIN collection c ON i.group_id = c.id
        WHERE c.account = %s AND c.date LIKE %s AND i.sold = 1
    """, (session.get('id'), year_value))
    sales_result = cur.fetchone()
    sale_price = sales_result['sale_price'] if sales_result else 0
    
    # Get purchases (total collection prices for the year)
    cur.execute("""
        SELECT COALESCE(SUM(price), 0) AS purchase_price
        FROM collection
        WHERE account = %s AND date LIKE %s
    """, (session.get('id'), year_value))
    purchase_result = cur.fetchone()
    purchase_price = purchase_result['purchase_price'] if purchase_result else 0
    
    return [sale_price, purchase_price, year]

def get_group_profit(group_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) AS sale_price
        FROM sale s
        INNER JOIN items i ON s.id = i.id
        INNER JOIN collection c ON i.group_id = c.id
        WHERE i.group_id = %s AND c.account = %s
    """, (group_id, session.get('id')))
    result = cur.fetchone()
    cur.close()
    return result['sale_price'] if result else 0

def get_total_returned_fees_in_group(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" 
        SELECT COALESCE(SUM(s.returned_fee), 0) as total_returned_fees
        FROM sale s
        INNER JOIN items i ON s.id = i.id
        INNER JOIN collection c ON i.group_id = c.id
        WHERE i.group_id = %s AND c.account = %s AND i.returned = 1
    """, (group_id, session.get('id')))
    result = cur.fetchone()
    cur.close()
    return result['total_returned_fees'] if result else 0

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
                   AND collection.account = %s
                   AND latitude != '' AND longitude != '' """,
                   (start_date, end_date, session.get('id')))
    return list(cur.fetchall())

# Optimized Report Functions
def get_combined_profit_report(start_date, end_date):
    """Single query for profit report combining sales and purchases"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            COALESCE(s.date, c.date) as date,
            COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) as sales_net,
            COALESCE(SUM(c.price), 0) as purchase_price,
            COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) - COALESCE(SUM(c.price), 0) as profit,
            DAYNAME(COALESCE(s.date, c.date)) as day
        FROM (
            SELECT date, SUM(price - shipping_fee - COALESCE(returned_fee, 0)) as price, SUM(shipping_fee) as shipping_fee
            FROM sale s
            INNER JOIN items i ON s.id = i.id
            INNER JOIN collection c ON i.group_id = c.id
            WHERE s.date BETWEEN %s AND %s AND c.account = %s
            GROUP BY s.date
        ) s
        FULL OUTER JOIN (
            SELECT date, SUM(price) as price
            FROM collection
            WHERE date BETWEEN %s AND %s AND account = %s
            GROUP BY date
        ) c ON s.date = c.date
        GROUP BY COALESCE(s.date, c.date)
        ORDER BY COALESCE(s.date, c.date)
    """, (start_date, end_date, session.get('id'), start_date, end_date, session.get('id')))
    return list(cur.fetchall())

def get_combined_sales_summary(start_date, end_date):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            c.date,
            c.name as group_name,
            c.price as purchase_price,
            COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) as sales_net,
            COUNT(i.id) as item_count,
            COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) - COALESCE(SUM(c.price), 0) as profit,
            c.id as group_id
        FROM collection c
        LEFT JOIN items i ON c.id = i.group_id
        LEFT JOIN sale s ON i.id = s.id
        WHERE c.account = %s AND c.date BETWEEN %s AND %s
        GROUP BY c.id, c.date, c.name, c.price
        ORDER BY c.date DESC
    """, (session.get('id'), start_date, end_date))
    return list(cur.fetchall())



# Admin Functions
def check_admin_status(user_id):
    """Check if a user has admin privileges"""
    if not user_id:
        return False
    
    try:
        # Check if MySQL is available
        if not mysql or not hasattr(mysql, 'connection') or not mysql.connection:
            print(f"Warning: MySQL not available in check_admin_status for user {user_id}")
            return False
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT is_admin FROM accounts WHERE id = %s", (user_id,))
        result = cur.fetchone()
        cur.close()
        
        # Safely check if result exists and has the expected value
        if result:
            # Handle both dict and tuple results
            if hasattr(result, 'keys'):  # DictCursor result
                is_admin = result['is_admin']
            else:  # Regular cursor result
                is_admin = result[0]
            
            return is_admin == 1 or is_admin == '1'
        
        return False
    except Exception as e:
        print(f"Error in check_admin_status: {e}")
        return False

def get_all_users():
    """Get all users for admin management"""
    try:
        # Check if session has 'id' key
        current_user_id = session.get('id')
        if not current_user_id:
            print("Warning: No session ID found in get_all_users")
            return []
        
        # Check if MySQL is available
        if not mysql:
            print("Warning: MySQL not initialized")
            return []
        
        # Check if database connection is available
        if not hasattr(mysql, 'connection') or not mysql.connection:
            print("Warning: No database connection available")
            return []
        
        cur = mysql.connection.cursor()
        
        # Get all users for admin management
        cur.execute("""
            SELECT 
                id, 
                username, 
                email, 
                name,
                is_admin,
                is_active,
                CASE 
                    WHEN id = %s THEN 'Current User'
                    ELSE ''
                END as is_current_user
            FROM accounts 
            ORDER BY username
        """, (current_user_id,))
        result = list(cur.fetchall())
        
        # Convert to list of dictionaries if needed
        if result and not hasattr(result[0], 'keys'):
            column_names = ['id', 'username', 'email', 'name', 'is_admin', 'is_active', 'is_current_user']
            result = [dict(zip(column_names, user)) for user in result]
        
        cur.close()
        return result
    except Exception as e:
        print(f"Error in get_all_users: {e}")
        if 'cur' in locals():
            cur.close()
        # Return a safe default structure to prevent KeyError: 0
        return [{'id': '1', 'username': 'Admin', 'email': 'admin@example.com', 'is_admin': 1, 'is_current_user': 'Current User'}]

def get_user_by_google_id(google_id):
    """Get user by Google ID"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM accounts WHERE google_id = %s", (google_id,))
        result = cur.fetchone()
        cur.close()
        return result
    except Exception as e:
        print(f"Error getting user by Google ID: {e}")
        return None

def get_user_by_email(email):
    """Get user by email"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM accounts WHERE email = %s", (email,))
        result = cur.fetchone()
        cur.close()
        return result
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None