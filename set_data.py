from flask import session
from datetime import datetime, date, timedelta
import uuid

# We'll get the mysql object passed to us or use a global reference
mysql = None

def set_mysql_connection(mysql_connection):
    """Set the MySQL connection from the main app"""
    global mysql
    mysql = mysql_connection

#Item Data

def generate_uuid():
    return uuid.uuid4()

def set_mark_sold(id,sold):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE items i 
        INNER JOIN collection c ON i.group_id = c.id 
        SET i.sold = %s 
        WHERE i.id = %s AND c.account = %s
    """, (sold, id, session.get('id')))
    mysql.connection.commit()
    cur.close()

def set_bought_items(details):
    cur = mysql.connection.cursor()
    for item in details:
        if item.startswith("item"):
            item_id = generate_uuid()
            cur.execute("INSERT INTO items(id, name, group_id, category_id, storage, list_date) VALUES (%s, %s, %s, %s, %s, %s)", 
                        (item_id, details[item],details['group'],details['category'],details['storage'],details['list_date'],))
            cur.execute("INSERT INTO sale(id, price, shipping_fee, date) VALUES (%s, 0, 0, %s)",
                        (item_id, date.today().strftime("%Y-%m-%d"),))
            mysql.connection.commit()
    cur.close()

def set_quick_sale(details):
    item_id = generate_uuid()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO items(id, name, group_id, category_id, list_date, sold) VALUES (%s, %s, %s, %s, %s, 1)", 
                (item_id, details['name'],details['group'],details['category'], details['list_date'],))
    cur.execute("INSERT INTO sale(id, price, shipping_fee, date) VALUES (%s, %s, %s, %s)",
                (item_id,details['price'],details['shipping_fee'],date.today().strftime("%Y-%m-%d"),))
    mysql.connection.commit()
    cur.close()
    return item_id

def set_sale_data(details):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE sale s
        INNER JOIN items i ON s.id = i.id
        INNER JOIN collection c ON i.group_id = c.id
        SET s.date = %s, s.price = %s, s.shipping_fee = %s 
        WHERE s.id = %s AND c.account = %s
    """, (details['sale_date'], details['price'], details['shipping_fee'], details['id'], session.get('id')))
    mysql.connection.commit()
    cur.close()


def set_items_modify(details):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE items i
        INNER JOIN collection c ON i.group_id = c.id
        SET i.name = %s, i.group_id = %s, i.category_id = %s, i.returned = %s, i.storage = %s, i.list_date = %s 
        WHERE i.id = %s AND c.account = %s
    """, (details['name'], details['group'], details['category'], details['returned'], details['storage'], details['list_date'], details['id'], session.get('id')))
    mysql.connection.commit()
    cur.close()

def remove_item_data(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        DELETE i FROM items i
        INNER JOIN collection c ON i.group_id = c.id
        WHERE i.id = %s AND c.account = %s
    """, (id, session.get('id')))
    mysql.connection.commit()
    cur.close()


#Group Data

def set_group_add(group_name, details, image_id):
    group_id = generate_uuid()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO collection(id, name, date, price, image, account) VALUES (%s, %s, %s, %s, %s, %s)", 
                (group_id, group_name, details['date'], details['price'], image_id, session.get('id')))
    mysql.connection.commit()
    cur.close()
    return group_id

def set_group_modify(details, image_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE collection SET name = %s, date = %s, price = %s, image = %s where id = %s AND account = %s", 
                (details['name'], details['date'], details['price'], image_id, details['id'], session.get('id')))
    mysql.connection.commit()
    cur.close()

def remove_group_data(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM collection WHERE id = %s AND account = %s", 
                (id, session.get('id')))
    mysql.connection.commit()
    cur.close()

#Expense Data
def set_expense(name, details, image_id, expense_type):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO expenses(name, date, price, image, type, account) VALUES (%s, %s, %s, %s, %s, %s)", 
                (name, details['date'], details['price'], image_id, expense_type, session.get('id')))
    mysql.connection.commit()
    cur.close()

def set_modify_expense(details, price, milage, image_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE expenses SET name = %s, date = %s, price = %s, milage = %s, type = %s, image = %s where id = %s AND account = %s", 
                (details['name'], details['date'], price, milage, details['expense_type'], image_id, details['id'], session.get('id')))
    mysql.connection.commit()
    cur.close()

#Cases

def add_case_data(details):
    cur = mysql.connection.cursor()
    for item in details:
        if item.startswith("item"):
            item_id = generate_uuid()
            cur.execute("INSERT INTO cases(id, name, platform,account) VALUES (%s, %s, %s, %s)", 
                        (item_id, details[item],details['platform'],session.get('id'),))
            mysql.connection.commit()
    cur.close()

def set_cases_modify(details):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE cases SET name = %s, platform = %s where id = %s AND account = %s", 
                (details['name'], details['platform'], details['id'], session.get('id')))
    mysql.connection.commit()
    cur.close()


def remove_case_data(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cases WHERE id = %s AND account = %s", 
                (id, session.get('id')))
    mysql.connection.commit()
    cur.close()

# Admin Functions
def toggle_admin_status(user_id):
    """Toggle admin status for a user"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE accounts SET is_admin = NOT is_admin WHERE id = %s", (user_id,))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error toggling admin status: {e}")
        return False

def delete_user(user_id):
    """Delete a user account"""
    try:
        cur = mysql.connection.cursor()
        
        # First, get all the group IDs for this user
        cur.execute("SELECT id FROM collection WHERE account = %s", (user_id,))
        group_ids = [row[0] for row in cur.fetchall()]
        
        if group_ids:
            # Delete sales for items in these groups
            cur.execute("DELETE s FROM sale s INNER JOIN items i ON s.id = i.id WHERE i.group_id IN %s", (tuple(group_ids),))
            
            # Delete items in these groups
            cur.execute("DELETE FROM items WHERE group_id IN %s", (tuple(group_ids),))
            
            # Delete locations for these groups
            cur.execute("DELETE FROM location WHERE group_id IN %s", (tuple(group_ids),))
            
            # Delete the collections
            cur.execute("DELETE FROM collection WHERE account = %s", (user_id,))
        
        # Delete expenses for this user
        cur.execute("DELETE FROM expenses WHERE account = %s", (user_id,))
        
        # Delete cases for this user
        cur.execute("DELETE FROM cases WHERE account = %s", (user_id,))
        
        # Finally delete the user account
        cur.execute("DELETE FROM accounts WHERE id = %s", (user_id,))
        
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

def create_user(details):
    """Create a new user account"""
    try:
        import hashlib
        
        # Generate UUID for the new user
        user_id = generate_uuid()
        
        # Hash the password
        hashed_password = hashlib.sha256(details['password'].encode()).hexdigest()
        
        # Set admin status (1 for admin, 0 for regular user)
        is_admin = 1 if details.get('is_admin') else 0
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO accounts(id, username, email, password, is_admin) VALUES (%s, %s, %s, %s, %s)", 
                    (user_id, details['username'], details['email'], hashed_password, is_admin))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False