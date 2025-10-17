import datetime
from datetime import date, timedelta
from flask import session

# MySQL connection will be set by app.py
mysql = None

def get_current_group_id():
    """Get the current user's group_id from session"""
    return session.get('group_id')

def get_current_user_id():
    """Get the current user's id from session"""
    return session.get('id')

def validate_string_input(value, max_length=100, default=''):
    """Validate and sanitize string inputs to prevent SQL injection"""
    if not isinstance(value, str):
        return default
    if len(value) > max_length:
        return default
    # Remove any potentially dangerous characters
    value = value.replace("'", "").replace('"', "").replace(';', "").replace('--', "")
    return value

def validate_numeric_input(value, min_val=None, max_val=None, default=0):
    """Validate and sanitize numeric inputs"""
    try:
        if isinstance(value, str):
            value = int(value)
        if min_val is not None and value < min_val:
            return default
        if max_val is not None and value > max_val:
            return default
        return value
    except (ValueError, TypeError):
        return default

def validate_date_input(value, default=None):
    """Validate and sanitize date inputs"""
    if default is None:
        default = str(datetime.date.today().year)
    
    if not isinstance(value, str):
        return default
    
    # Basic date format validation
    if len(value) > 10:  # YYYY-MM-DD is 10 chars
        return default
    
    # Check if it's a valid date format
    try:
        datetime.datetime.strptime(value, '%Y-%m-%d')
        return value
    except ValueError:
        try:
            datetime.datetime.strptime(value, '%Y')
            return value
        except ValueError:
            return default

# We'll get the mysql object passed to us or use a global reference
mysql = None

def set_mysql_connection(mysql_connection):
    """Set the MySQL connection from the main app"""
    global mysql
    mysql = mysql_connection

#Get Years
def get_years():
    """Get all years from collection data"""
    try:
        cur = mysql.connection.cursor()
        
        # Get the current group_id, but handle the case where it might be None
        group_id = get_current_group_id()
        if not group_id:
            # If no group_id in session, try to get years from all collections
            # This is a fallback for when the user might not be logged in yet
            cur.execute("""
                SELECT DISTINCT YEAR(date) as year
                FROM collection
                WHERE date IS NOT NULL
                ORDER BY year DESC
            """)
        else:
            cur.execute("""
                SELECT DISTINCT YEAR(date) as year
                FROM collection
                WHERE group_id = %s AND date IS NOT NULL
                ORDER BY year DESC
            """, (group_id,))
        
        years = cur.fetchall()
        cur.close()
        return years
    except Exception as e:
        print(f"Error in get_years: {e}")
        return []

#Group Data
def get_all_from_group(group_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM collection WHERE id = %s AND group_id = %s", (group_id, get_current_group_id()))
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
        WHERE c.date LIKE %s AND c.group_id = %s
        GROUP BY c.id, c.name, c.price, c.date, c.location_address
        ORDER BY c.date
    """, (date, get_current_group_id()))
    return list(cur.fetchall())

def get_all_from_group_and_items_by_name(name):
    # Use validation function
    validated_name = validate_string_input(name, max_length=100)
    search_pattern = '%{}%'.format(validated_name)
    
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
        WHERE c.name LIKE %s AND c.group_id = %s
        GROUP BY c.id, c.name, c.price, c.date, c.location_address
        ORDER BY c.date
    """, (search_pattern, get_current_group_id()))
    return list(cur.fetchall())

def get_all_from_groups(date):
    cur = mysql.connection.cursor()
    
    # Handle wildcard case - if date is '%', get all groups regardless of date
    if date == '%':
        cur.execute("SELECT * FROM collection WHERE collection.group_id = %s ORDER BY name ASC", 
                   (get_current_group_id(),))
    else:
        # Use validation function for specific dates
        validated_date = validate_date_input(date)
        search_pattern = '%{}%'.format(validated_date)
        cur.execute("SELECT * FROM collection WHERE date LIKE %s AND collection.group_id = %s ORDER BY name ASC", 
                   (search_pattern, get_current_group_id()))
    
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
        start_date = "{}-01-01".format(year)
        end_date = "{}-01-01".format(int(year) + 1)
    
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
                    collection.location_address,
                    collection.account
                    FROM collection collection
                    WHERE collection.id = %s AND collection.group_id = %s""", (group_id, get_current_group_id()))
    return list(cur.fetchall())

def get_group_sold_from_date(start_date, end_date):
    """Optimized group sales report query"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            c.date,
            COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) AS net
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
            COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) AS net,
            DAYNAME(c.date) AS day
        FROM collection c
        LEFT JOIN items i ON c.id = i.group_id
        LEFT JOIN sale s ON i.id = s.id
        WHERE DAYOFWEEK(c.date) = %s 
        AND c.group_id = %s 
        GROUP BY c.date 
        ORDER BY c.date
    """, (day, get_current_group_id()))
    return list(cur.fetchall())

#Item Data
def get_group_id(item_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT i.group_id 
        FROM items i 
        INNER JOIN collection c ON i.group_id = c.id 
        WHERE i.id = %s AND c.group_id = %s
    """, (item_id, get_current_group_id()))
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

def get_list_of_items_with_name(name, sold):
    # Use validation functions
    validated_name = validate_string_input(name, max_length=100)
    validated_sold = validate_numeric_input(sold, min_val=0, max_val=1, default='')
    
    search_pattern = '%{}%'.format(validated_name)
    cur = mysql.connection.cursor()
    
    cur.execute("""SELECT 
                items.name, 
                items.sold,
                items.id,
                items.storage,
                items.ebay_item_id,
                items.returned,
                items.list_date,
                COALESCE(categories.uuid_id, items.category_id) AS category_id,
                sale.price AS gross_price,
                sale.shipping_fee AS shipping_fee,
                sale.date AS sale_date,
                (sale.price - sale.shipping_fee) AS net,
                collection.id as group_id,
                collection.name as group_name
                FROM items items 
                INNER JOIN collection collection ON items.group_id = collection.id
                LEFT JOIN sale sale ON items.id = sale.id
                LEFT JOIN categories ON items.category_id = categories.id
                WHERE items.name LIKE %s AND collection.group_id = %s""", 
                (search_pattern, get_current_group_id()))
    
    all_items = list(cur.fetchall())
    
    # Now filter by sold status if needed
    if validated_sold != '%':
        # Handle empty string case - treat as "not sold" (0)
        if validated_sold == '':
            filtered_items = [item for item in all_items if str(item['sold']) == '0']
        else:
            filtered_items = [item for item in all_items if str(item['sold']) == str(validated_sold)]
        return filtered_items
    else:
        return all_items

def get_data_from_item_groups(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    items.name, 
                    items.sold, 
                    items.id,
                    COALESCE(categories.uuid_id, items.category_id) AS category_id,
                    items.storage,
                    items.returned,
                    items.ebay_item_id,
                    sale.price AS gross,
                    sale.shipping_fee AS shipping_fee,
                    sale.returned_fee AS returned_fee,
                    (sale.price - sale.shipping_fee - COALESCE(sale.returned_fee, 0)) AS net,
                    sale.date AS sale_date,
					DATEDIFF(sale.date,collection.date) AS days_to_sell 
                    FROM items items
                    INNER JOIN collection collection ON items.group_id = collection.id
                    LEFT JOIN sale sale ON sale.id = items.id
                    LEFT JOIN categories ON items.category_id = categories.id
                    WHERE items.group_id = %s AND collection.group_id = %s
                    ORDER BY sale.date""", (group_id, get_current_group_id()))
    return list(cur.fetchall())

def get_total_items_in_group(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" 
        SELECT count(*) as total 
        FROM items i 
        INNER JOIN collection c ON i.group_id = c.id 
        WHERE i.group_id = %s AND c.group_id = %s
    """, (group_id, get_current_group_id()))
    return cur.fetchone()

def get_total_items_in_group_sold(group_id):
    cur = mysql.connection.cursor()
    cur.execute(""" 
        SELECT count(*) as total 
        FROM items i 
        INNER JOIN collection c ON i.group_id = c.id 
        WHERE i.group_id = %s AND i.sold = 1 AND c.group_id = %s
    """, (group_id, get_current_group_id()))
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
        AND c.group_id = %s 
        GROUP BY s.date 
        ORDER BY s.date ASC
    """, (start_date, end_date, get_current_group_id()))
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
        AND c.group_id = %s 
        GROUP BY s.date 
        ORDER BY s.date ASC
    """, (day, get_current_group_id()))
    return list(cur.fetchall())

def get_data_for_item_describe(item_id):
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT 
                    items.name, 
                    items.sold, 
                    items.id,
                    items.group_id,
                    COALESCE(categories.uuid_id, items.category_id) AS category_id,
                    items.returned,
                    items.storage,
                    items.list_date,
                    items.ebay_item_id,
                    collection.name AS group_name,
                    collection.date AS purchase_date
                    FROM items items
                    INNER JOIN collection collection ON items.group_id = collection.id
                    LEFT JOIN categories ON items.category_id = categories.id
                    WHERE items.id = %s AND collection.group_id = %s""", (item_id, get_current_group_id()))
    return list(cur.fetchall())

def get_all_items_not_sold():
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT 
                * FROM items items 
                INNER JOIN collection collection ON items.group_id = collection.id  
                WHERE items.sold = 0 AND collection.group_id = %s ORDER BY items.name ASC""", (get_current_group_id(), ))
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
                    WHERE items.sold = 1 AND collection.group_id = %s ORDER BY sale.date ASC""", (get_current_group_id(), ))
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
                    categories.uuid_id AS category_id,
                    sale.date as sales_date,
                    collection.date
                    FROM items items 
                    INNER JOIN collection collection ON items.group_id = collection.id
                    INNER JOIN sale sale ON items.id = sale.id
                    INNER JOIN categories categories ON items.category_id = categories.uuid_id
                    WHERE categories.uuid_id = %s AND collection.group_id = %s
                    ORDER BY categories.uuid_id""",
                    (category_id, get_current_group_id(), ))
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
            INNER JOIN categories cat ON i.category_id = cat.uuid_id
            WHERE c.account = %s
            AND cat.uuid_id = %s
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
            INNER JOIN categories cat ON i.category_id = cat.uuid_id
            WHERE c.account = %s
            AND cat.uuid_id = %s
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
            INNER JOIN categories cat ON i.category_id = cat.uuid_id
            WHERE c.account = %s
            AND cat.uuid_id = %s
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
    user_id = session.get('id')
    if not user_id:
        return []
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT uuid_id as id, type, user_id FROM categories WHERE user_id = %s ORDER BY type", (user_id,))
    return list(cur.fetchall())

def get_category(category_id):
    user_id = session.get('id')
    if not user_id:
        return None
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT type FROM categories where uuid_id = %s AND user_id = %s", (category_id, user_id))
    return cur.fetchone()

def get_category_by_id(category_id):
    """Get category by ID without user restriction (for admin purposes)"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT uuid_id as id, type, user_id FROM categories where uuid_id = %s", (category_id,))
    return cur.fetchone()

def get_category_item_counts():
    """Get the count of items in each category for the current user"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            c.uuid_id as id,
            c.type,
            COUNT(CASE WHEN col.account = %s THEN i.id ELSE NULL END) as item_count
        FROM categories c
        LEFT JOIN items i ON c.uuid_id = i.category_id
        LEFT JOIN collection col ON i.group_id = col.id
        WHERE c.user_id = %s
        GROUP BY c.uuid_id, c.type
        ORDER BY c.type
    """, (session.get('id'), session.get('id')))
    return list(cur.fetchall())



#Profit Data
def get_profit(year):
    year_value = str(year) + '-%-%'
    cur = mysql.connection.cursor()
    
    # Get sales (only for sold items, including returned fees)
    cur.execute("""
        SELECT COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) AS sale_price
        FROM sale s
        INNER JOIN items i ON s.id = i.id
        INNER JOIN collection c ON i.group_id = c.id
        WHERE c.group_id = %s AND c.date LIKE %s AND i.sold = 1
    """, (get_current_group_id(), year_value))
    sales_result = cur.fetchone()
    sale_price = sales_result['sale_price'] if sales_result else 0
    
    # Get purchases (total collection prices for the year)
    cur.execute("""
        SELECT COALESCE(SUM(price), 0) AS purchase_price
        FROM collection
        WHERE group_id = %s AND date LIKE %s
    """, (get_current_group_id(), year_value))
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
        WHERE i.group_id = %s AND c.group_id = %s
    """, (group_id, get_current_group_id()))
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
        WHERE i.group_id = %s AND c.group_id = %s AND i.returned = 1
    """, (group_id, get_current_group_id()))
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
                   AND collection.group_id = %s
                   AND latitude != '' AND longitude != '' """,
                   (start_date, end_date, get_current_group_id()))
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

def get_purchases_by_city(city, year='all'):
    """Get all purchases made in a specific city, optionally filtered by year"""
    cur = mysql.connection.cursor()
    
    # Build the year filter
    year_filter = ""
    params = [get_current_group_id(), city, f'%, {city},%', f'%, {city} %', f'%, {city}, %']
    
    if year != 'all':
        year_filter = "AND c.date LIKE %s"
        params.append(f'{year}-%-%')
    
    cur.execute(f"""
        SELECT 
            c.id,
            c.name,
            c.date,
            c.price,
            c.location_name,
            c.location_address,
            c.latitude,
            c.longitude,
            COUNT(i.id) as item_count,
            SUM(CASE WHEN i.sold = 1 THEN 1 ELSE 0 END) as sold_count,
            COALESCE(SUM(CASE WHEN i.sold = 1 THEN s.price - s.shipping_fee - COALESCE(s.returned_fee, 0) ELSE 0 END), 0) as total_sales,
            COALESCE(SUM(CASE WHEN i.sold = 1 THEN s.price - s.shipping_fee - COALESCE(s.returned_fee, 0) ELSE 0 END), 0) - c.price as profit
        FROM collection c
        LEFT JOIN items i ON c.id = i.group_id
        LEFT JOIN sale s ON i.id = s.id
        WHERE c.group_id = %s 
        AND (
            c.location_name = %s 
            OR c.location_address LIKE %s
            OR c.location_address LIKE %s
            OR c.location_address LIKE %s
        )
        {year_filter}
        GROUP BY c.id, c.name, c.date, c.price, c.location_name, c.location_address, c.latitude, c.longitude
        ORDER BY c.date DESC
    """, params)
    results = cur.fetchall()
    return list(results)

def get_city_summary(city, year='all'):
    """Get summary statistics for purchases in a specific city, optionally filtered by year"""
    cur = mysql.connection.cursor()
    
    # Build the year filter
    year_filter = ""
    params = [get_current_group_id(), city, f'%, {city},%', f'%, {city} %', f'%, {city}, %']
    
    if year != 'all':
        year_filter = "AND c.date LIKE %s"
        params.append(f'{year}-%-%')
    
    # First get the total spent from collection table only (no joins)
    cur.execute(f"""
        SELECT 
            COUNT(DISTINCT c.id) as total_purchases,
            SUM(c.price) as total_spent,
            MIN(c.date) as first_purchase,
            MAX(c.date) as last_purchase
        FROM collection c
        WHERE c.group_id = %s 
        AND (
            c.location_name = %s 
            OR c.location_address LIKE %s
            OR c.location_address LIKE %s
            OR c.location_address LIKE %s
        )
        {year_filter}
    """, params)
    
    collection_result = cur.fetchone()
    
    # Then get item and sales data
    cur.execute(f"""
        SELECT 
            COUNT(i.id) as total_items,
            SUM(CASE WHEN i.sold = 1 THEN 1 ELSE 0 END) as sold_items,
            COALESCE(SUM(CASE WHEN i.sold = 1 THEN s.price - s.shipping_fee - COALESCE(s.returned_fee, 0) ELSE 0 END), 0) as total_sales
        FROM collection c
        LEFT JOIN items i ON c.id = i.group_id
        LEFT JOIN sale s ON i.id = s.id
        WHERE c.group_id = %s 
        AND (
            c.location_name = %s 
            OR c.location_address LIKE %s
            OR c.location_address LIKE %s
            OR c.location_address LIKE %s
        )
        {year_filter}
    """, params)
    
    items_result = cur.fetchone()
    
    # Combine results
    if collection_result and items_result:
        # Handle None values by converting them to 0
        total_spent = collection_result['total_spent'] or 0
        total_sales = items_result['total_sales'] or 0
        total_items = items_result['total_items'] or 0
        sold_items = items_result['sold_items'] or 0
        total_purchases = collection_result['total_purchases'] or 0
        
        result = {
            'total_purchases': total_purchases,
            'total_spent': total_spent,
            'total_items': total_items,
            'sold_items': sold_items,
            'total_sales': total_sales,
            'total_profit': total_sales - total_spent,
            'first_purchase': collection_result['first_purchase'],
            'last_purchase': collection_result['last_purchase']
        }
        return result
    
    # If no results found, return a default result with zeros
    return {
        'total_purchases': 0,
        'total_spent': 0,
        'total_items': 0,
        'sold_items': 0,
        'total_sales': 0,
        'total_profit': 0,
        'first_purchase': None,
        'last_purchase': None
    }

def get_all_cities():
    """Get all unique cities from group's purchases"""
    cur = mysql.connection.cursor()
    # First, let's see what we're getting before filtering
    cur.execute("""
        SELECT DISTINCT 
            CASE 
                WHEN c.location_name IS NOT NULL AND c.location_name != '' THEN c.location_name
                WHEN c.location_address IS NOT NULL AND c.location_address != '' THEN 
                    CASE 
                        -- For addresses with exactly 3 comma-separated parts, take the middle one (most common case)
                        WHEN (LENGTH(c.location_address) - LENGTH(REPLACE(c.location_address, ',', ''))) = 2 THEN
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -2), ',', 1))
                        -- For addresses with 4+ comma-separated parts, try different positions
                        WHEN (LENGTH(c.location_address) - LENGTH(REPLACE(c.location_address, ',', ''))) >= 3 THEN
                            CASE 
                                -- Try third-to-last part first
                                WHEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -3), ',', 1)) REGEXP '^[A-Za-z][A-Za-z ]+[A-Za-z]$' THEN
                                    TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -3), ',', 1))
                                -- Fallback to second-to-last part
                                ELSE TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -2), ',', 1))
                            END
                        -- For addresses with only 2 comma-separated parts, take the first part
                        WHEN (LENGTH(c.location_address) - LENGTH(REPLACE(c.location_address, ',', ''))) = 1 THEN
                            TRIM(SUBSTRING_INDEX(c.location_address, ',', 1))
                        -- Fallback: try the second-to-last comma-separated part
                        ELSE 
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -2), ',', 1))
                    END
                ELSE NULL
            END as city_name,
            COUNT(c.id) as purchase_count,
            SUM(c.price) as total_spent
        FROM collection c
        WHERE c.group_id = %s 
        AND (c.location_name IS NOT NULL AND c.location_name != '' 
             OR c.location_address IS NOT NULL AND c.location_address != '')
        GROUP BY city_name
        HAVING city_name IS NOT NULL AND city_name != ''
        AND city_name NOT REGEXP '^[0-9]+$'
        AND city_name NOT REGEXP '^[A-Z]{2}$'
        AND city_name NOT REGEXP '^[0-9]{5}$'
        AND city_name NOT REGEXP '^[A-Z]{2} [0-9]{5}$'
        AND city_name NOT LIKE 'None'
        AND city_name NOT LIKE 'NULL'
        AND city_name NOT LIKE 'null'
        AND city_name NOT LIKE 'Unknown'
        AND city_name NOT LIKE 'unknown'
        AND LENGTH(city_name) > 2
        ORDER BY city_name ASC
    """, (get_current_group_id(),))
    
    results = cur.fetchall()
    return results

def get_all_states():
    """Get all unique states from group's purchases"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DISTINCT 
            CASE 
                WHEN c.location_name IS NOT NULL AND c.location_name != '' AND c.location_name != 'None' THEN 
                    CASE 
                        WHEN (LENGTH(c.location_name) - LENGTH(REPLACE(c.location_name, ',', ''))) = 2 THEN
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_name, ',', -1), ',', 1))
                        WHEN (LENGTH(c.location_name) - LENGTH(REPLACE(c.location_name, ',', ''))) >= 3 THEN
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_name, ',', -2), ',', 1))
                        ELSE TRIM(SUBSTRING_INDEX(c.location_name, ',', -1))
                    END
                WHEN c.location_address IS NOT NULL AND c.location_address != '' THEN 
                    CASE 
                        WHEN (LENGTH(c.location_address) - LENGTH(REPLACE(c.location_address, ',', ''))) = 2 THEN
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -1), ',', 1))
                        WHEN (LENGTH(c.location_address) - LENGTH(REPLACE(c.location_address, ',', ''))) >= 3 THEN
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -2), ',', 1))
                        ELSE TRIM(SUBSTRING_INDEX(c.location_address, ',', -1))
                    END
                ELSE NULL
            END as raw_state,
            CASE 
                WHEN c.location_name IS NOT NULL AND c.location_name != '' AND c.location_name != 'None' THEN 
                    CASE 
                        WHEN (LENGTH(c.location_name) - LENGTH(REPLACE(c.location_name, ',', ''))) = 2 THEN
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_name, ',', -1), ',', 1))
                        WHEN (LENGTH(c.location_name) - LENGTH(REPLACE(c.location_name, ',', ''))) >= 3 THEN
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_name, ',', -2), ',', 1))
                        ELSE TRIM(SUBSTRING_INDEX(c.location_name, ',', -1))
                    END
                WHEN c.location_address IS NOT NULL AND c.location_address != '' THEN 
                    CASE 
                        WHEN (LENGTH(c.location_address) - LENGTH(REPLACE(c.location_address, ',', ''))) = 2 THEN
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -1), ',', 1))
                        WHEN (LENGTH(c.location_address) - LENGTH(REPLACE(c.location_address, ',', ''))) >= 3 THEN
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -2), ',', 1))
                        ELSE TRIM(SUBSTRING_INDEX(c.location_address, ',', -1))
                    END
                ELSE NULL
            END as state_name,
            COUNT(c.id) as purchase_count,
            SUM(c.price) as total_spent
        FROM collection c
        WHERE c.group_id = %s 
        AND (c.location_name IS NOT NULL AND c.location_name != '' AND c.location_name != 'None'
             OR c.location_address IS NOT NULL AND c.location_address != '')
        GROUP BY state_name
        HAVING state_name IS NOT NULL AND state_name != '' AND state_name != 'None'
        AND (
            state_name REGEXP '^[A-Z]{2}$' OR  -- 2-letter state codes
            state_name REGEXP '^[A-Z]{2} [0-9]{5}$' OR  -- 2-letter state codes with zip
            state_name REGEXP '^[A-Za-z][A-Za-z ]+[A-Za-z]$'  -- Full state names
        )
        ORDER BY state_name ASC
    """, (get_current_group_id(),))
    
    results = cur.fetchall()
    
    # Process results to extract only state codes (remove zip codes)
    processed_results = []
    seen_states = set()
    
    for result in results:
        raw_state = result['raw_state']
        if raw_state:
            # Extract only the state code (first 2 letters)
            if raw_state.startswith('TX ') or raw_state.startswith('CA ') or raw_state.startswith('NY ') or raw_state.startswith('FL '):
                state_code = raw_state[:2]
            elif len(raw_state) >= 2 and raw_state[:2].isalpha():
                state_code = raw_state[:2]
            else:
                state_code = raw_state
            
            # Only add unique states
            if state_code not in seen_states and len(state_code) == 2 and state_code.isalpha():
                seen_states.add(state_code)
                processed_results.append({
                    'state_name': state_code,
                    'purchase_count': result['purchase_count'],
                    'total_spent': result['total_spent']
                })
    
    return processed_results

def get_cities_by_state(state):
    """Get all unique cities from group's purchases for a specific state"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DISTINCT 
            CASE 
                WHEN c.location_name IS NOT NULL AND c.location_name != '' AND c.location_name != 'None' THEN 
                    CASE 
                        WHEN (LENGTH(c.location_name) - LENGTH(REPLACE(c.location_name, ',', ''))) = 2 THEN
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_name, ',', -2), ',', 1))
                        WHEN (LENGTH(c.location_name) - LENGTH(REPLACE(c.location_name, ',', ''))) >= 3 THEN
                            CASE 
                                WHEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_name, ',', -3), ',', 1)) REGEXP '^[A-Za-z][A-Za-z ]+[A-Za-z]$' THEN
                                    TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_name, ',', -3), ',', 1))
                                ELSE TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_name, ',', -2), ',', 1))
                            END
                        WHEN (LENGTH(c.location_name) - LENGTH(REPLACE(c.location_name, ',', ''))) = 1 THEN
                            TRIM(SUBSTRING_INDEX(c.location_name, ',', 1))
                        ELSE 
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_name, ',', -2), ',', 1))
                    END
                WHEN c.location_address IS NOT NULL AND c.location_address != '' THEN 
                    CASE 
                        WHEN (LENGTH(c.location_address) - LENGTH(REPLACE(c.location_address, ',', ''))) = 2 THEN
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -2), ',', 1))
                        WHEN (LENGTH(c.location_address) - LENGTH(REPLACE(c.location_address, ',', ''))) >= 3 THEN
                            CASE 
                                WHEN TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -3), ',', 1)) REGEXP '^[A-Za-z][A-Za-z ]+[A-Za-z]$' THEN
                                    TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -3), ',', 1))
                                ELSE TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -2), ',', 1))
                            END
                        WHEN (LENGTH(c.location_address) - LENGTH(REPLACE(c.location_address, ',', ''))) = 1 THEN
                            TRIM(SUBSTRING_INDEX(c.location_address, ',', 1))
                        ELSE 
                            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(c.location_address, ',', -2), ',', 1))
                    END
                ELSE NULL
            END as city_name,
            COUNT(c.id) as purchase_count,
            SUM(c.price) as total_spent
        FROM collection c
        WHERE c.group_id = %s 
        AND (c.location_name IS NOT NULL AND c.location_name != '' AND c.location_name != 'None'
             OR c.location_address IS NOT NULL AND c.location_address != '')
        AND (
            (c.location_name LIKE %s OR c.location_address LIKE %s) OR
            (c.location_name LIKE %s OR c.location_address LIKE %s) OR
            (c.location_name LIKE %s OR c.location_address LIKE %s) OR
            (c.location_name LIKE %s OR c.location_address LIKE %s)
        )
        GROUP BY city_name
        HAVING city_name IS NOT NULL AND city_name != '' AND city_name != 'None'
        AND city_name NOT REGEXP '^[0-9]+$'
        AND city_name NOT REGEXP '^[A-Z]{2}$'
        AND city_name NOT REGEXP '^[0-9]{5}$'
        AND city_name NOT REGEXP '^[A-Z]{2} [0-9]{5}$'
        AND city_name NOT LIKE 'NULL'
        AND city_name NOT LIKE 'null'
        AND city_name NOT LIKE 'Unknown'
        AND city_name NOT LIKE 'unknown'
        AND LENGTH(city_name) > 2
        ORDER BY city_name ASC
    """, (get_current_group_id(), f'%, {state}', f'%, {state}', f'%, {state},%', f'%, {state},%', f'%, {state} %', f'%, {state} %', f'%, {state}, %', f'%, {state}, %'))
    
    results = cur.fetchall()
    return results

# Admin Functions
def check_admin_status(user_id):
    """Check if a user has admin privileges"""
    if not user_id:
        return False
    
    try:
        # Check if MySQL is available
        if not mysql or not hasattr(mysql, 'connection') or not mysql.connection:
            print("Warning: MySQL not available in check_admin_status for user {}".format(user_id))
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
        print("Error in check_admin_status: {}".format(e))
        return False

def get_all_users():
    """Get all users for admin management"""
    try:
        # Check if MySQL is available
        if not mysql:
            print("Warning: MySQL not initialized")
            return []
        
        # Check if database connection is available
        if not hasattr(mysql, 'connection') or not mysql.connection:
            print("Warning: No database connection available")
            return []
        
        cur = mysql.connection.cursor()
        
        # Get current user ID from session if available (for highlighting current user)
        current_user_id = session.get('id') if session else None
        
        # Get all users for admin management with group information
        cur.execute("""
            SELECT 
                a.id, 
                a.username, 
                a.email, 
                a.name,
                a.is_admin,
                a.is_active,
                a.group_id,
                g.name as group_name,
                CASE 
                    WHEN a.id = %s THEN 'Current User'
                    ELSE ''
                END as is_current_user
            FROM accounts a
            LEFT JOIN `groups` g ON a.group_id = g.id
            ORDER BY a.username
        """, (current_user_id,))
        result = list(cur.fetchall())
        
        # Convert to list of dictionaries if needed
        if result and not hasattr(result[0], 'keys'):
            column_names = ['id', 'username', 'email', 'name', 'is_admin', 'is_active', 'group_id', 'group_name', 'is_current_user']
            result = [dict(zip(column_names, user)) for user in result]
        
        cur.close()
        return result
    except Exception as e:
        print("Error in get_all_users: {}".format(e))
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
        print("Error getting user by Google ID: {}".format(e))
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
        print("Error getting user by email: {}".format(e))
        return None

# Group Management Functions
def get_all_groups():
    """Get all groups for admin management"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT g.*, COUNT(a.id) as member_count
        FROM `groups` g
        LEFT JOIN accounts a ON g.id = a.group_id
        GROUP BY g.id
        ORDER BY g.name
    """)
    return list(cur.fetchall())

def get_group_by_id(group_id):
    """Get group details by ID"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `groups` WHERE id = %s", (group_id,))
    return cur.fetchone()

def get_group_members(group_id):
    """Get all members of a specific group"""
    try:
        cur = mysql.connection.cursor()
        
        # Get current user ID from session if available
        current_user_id = session.get('id') if session else None
        
        cur.execute("""
            SELECT 
                a.id, 
                a.username, 
                a.email, 
                a.name,
                a.is_admin,
                a.is_active,
                a.group_id,
                g.name as group_name,
                CASE 
                    WHEN a.id = %s THEN 'Current User'
                    ELSE ''
                END as is_current_user
            FROM accounts a
            INNER JOIN `groups` g ON a.group_id = g.id
            WHERE a.group_id = %s
            ORDER BY a.username
        """, (current_user_id, group_id))
        
        result = list(cur.fetchall())
        
        # Convert to list of dictionaries if needed
        if result and not hasattr(result[0], 'keys'):
            column_names = ['id', 'username', 'email', 'name', 'is_admin', 'is_active', 'group_id', 'group_name', 'is_current_user']
            result = [dict(zip(column_names, user)) for user in result]
        
        cur.close()
        return result
    except Exception as e:
        print("Error in get_group_members: {}".format(e))
        if 'cur' in locals():
            cur.close()
        return []

def get_group_creator(group_id):
    """Get the creator of the collection/group using the account field from group data"""
    try:
        cur = mysql.connection.cursor()
        
        # Get the account ID from the group data (who created the collection)
        cur.execute("""
            SELECT DISTINCT
                c.account as created_by,
                a.username as creator_username,
                a.name as creator_name,
                a.email as creator_email
            FROM `collection` c
            LEFT JOIN accounts a ON c.account = a.id
            WHERE c.id = %s AND c.account IS NOT NULL
            LIMIT 1
        """, (group_id,))
        result = cur.fetchone()
        
        cur.close()
        
        return result
    except Exception as e:
        print("Error in get_group_creator: {}".format(e))
        if 'cur' in locals():
            cur.close()
        return None

def get_current_group_info():
    """Get current user's group information"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT g.*, COUNT(a.id) as member_count
        FROM `groups` g
        LEFT JOIN accounts a ON g.id = a.group_id
        WHERE g.id = %s
        GROUP BY g.id
    """, (get_current_group_id(),))
    return cur.fetchone()

# Neighborhood Functions
def get_user_neighborhoods():
    """Get all neighborhoods for the current user"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, name, description, city, state, score, created_at, updated_at
            FROM neighborhoods
            WHERE user_id = %s
            ORDER BY name ASC
        """, (session.get('id'),))
        return list(cur.fetchall())
    except Exception as e:
        print("Error in get_user_neighborhoods: {}".format(e))
        return []
    finally:
        if 'cur' in locals():
            cur.close()

def get_neighborhood_by_id(neighborhood_id):
    """Get a specific neighborhood by ID"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, name, description, city, state, score, created_at, updated_at
            FROM neighborhoods
            WHERE id = %s AND user_id = %s
        """, (neighborhood_id, session.get('id')))
        return cur.fetchone()
    except Exception as e:
        print("Error in get_neighborhood_by_id: {}".format(e))
        return None
    finally:
        if 'cur' in locals():
            cur.close()

def get_neighborhood_purchases(neighborhood_id, year='all'):
    """Get purchases for a specific neighborhood"""
    try:
        cur = mysql.connection.cursor()
        
        if year == 'all':
            cur.execute("""
                SELECT 
                    c.id,
                    c.name,
                    c.date,
                    c.price,
                    c.location_address,
                    c.latitude,
                    c.longitude,
                    COUNT(i.id) as item_count,
                    SUM(CASE WHEN i.sold = 1 THEN 1 ELSE 0 END) as sold_count,
                    COALESCE(SUM(s.price), 0) as total_sales,
                    COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) as total_profit
                FROM collection c
                LEFT JOIN items i ON c.id = i.group_id
                LEFT JOIN sale s ON i.id = s.id
                WHERE c.neighborhood_id = %s AND c.group_id = %s
                GROUP BY c.id, c.name, c.date, c.price, c.location_address, c.latitude, c.longitude
                ORDER BY c.date DESC
            """, (neighborhood_id, get_current_group_id()))
        else:
            cur.execute("""
                SELECT 
                    c.id,
                    c.name,
                    c.date,
                    c.price,
                    c.location_address,
                    c.latitude,
                    c.longitude,
                    COUNT(i.id) as item_count,
                    SUM(CASE WHEN i.sold = 1 THEN 1 ELSE 0 END) as sold_count,
                    COALESCE(SUM(s.price), 0) as total_sales,
                    COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) as total_profit
                FROM collection c
                LEFT JOIN items i ON c.id = i.group_id
                LEFT JOIN sale s ON i.id = s.id
                WHERE c.neighborhood_id = %s AND c.group_id = %s AND YEAR(c.date) = %s
                GROUP BY c.id, c.name, c.date, c.price, c.location_address, c.latitude, c.longitude
                ORDER BY c.date DESC
            """, (neighborhood_id, get_current_group_id(), year))
        
        return list(cur.fetchall())
    except Exception as e:
        print("Error in get_neighborhood_purchases: {}".format(e))
        return []
    finally:
        if 'cur' in locals():
            cur.close()

def get_neighborhood_summary(neighborhood_id, year='all'):
    """Get summary statistics for a neighborhood"""
    try:
        cur = mysql.connection.cursor()
        
        if year == 'all':
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT c.id) as total_purchases,
                    COALESCE(SUM(c.price), 0) as total_spent,
                    COUNT(i.id) as total_items,
                    SUM(CASE WHEN i.sold = 1 THEN 1 ELSE 0 END) as sold_items,
                    COALESCE(SUM(s.price), 0) as total_sales,
                    COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) as total_profit,
                    MIN(c.date) as first_purchase,
                    MAX(c.date) as last_purchase
                FROM collection c
                LEFT JOIN items i ON c.id = i.group_id
                LEFT JOIN sale s ON i.id = s.id
                WHERE c.neighborhood_id = %s AND c.group_id = %s
            """, (neighborhood_id, get_current_group_id()))
        else:
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT c.id) as total_purchases,
                    COALESCE(SUM(c.price), 0) as total_spent,
                    COUNT(i.id) as total_items,
                    SUM(CASE WHEN i.sold = 1 THEN 1 ELSE 0 END) as sold_items,
                    COALESCE(SUM(s.price), 0) as total_sales,
                    COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0)), 0) as total_profit,
                    MIN(c.date) as first_purchase,
                    MAX(c.date) as last_purchase
                FROM collection c
                LEFT JOIN items i ON c.id = i.group_id
                LEFT JOIN sale s ON i.id = s.id
                WHERE c.neighborhood_id = %s AND c.group_id = %s AND YEAR(c.date) = %s
            """, (neighborhood_id, get_current_group_id(), year))
        
        return cur.fetchone()
    except Exception as e:
        print("Error in get_neighborhood_summary: {}".format(e))
        return None
    finally:
        if 'cur' in locals():
            cur.close()

def get_neighborhood_years(neighborhood_id):
    """Get all years with purchases for a neighborhood"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT DISTINCT YEAR(date) as year
            FROM collection
            WHERE neighborhood_id = %s AND group_id = %s
            ORDER BY year DESC
        """, (neighborhood_id, get_current_group_id()))
        return list(cur.fetchall())
    except Exception as e:
        print("Error in get_neighborhood_years: {}".format(e))
        return []
    finally:
        if 'cur' in locals():
            cur.close()