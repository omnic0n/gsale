from flask import session
import datetime
from datetime import date, timedelta
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

def set_mark_sold(id, sold):
    # Validate inputs
    if not isinstance(id, str) or len(id) > 50:
        raise ValueError("Invalid item ID")
    
    if sold not in [0, 1]:
        raise ValueError("Invalid sold status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE items i 
        INNER JOIN collection c ON i.group_id = c.id 
        SET i.sold = %s 
        WHERE i.id = %s AND c.account = %s
    """, (sold, id, session.get('id')))
    mysql.connection.commit()
    cur.close()

def set_bought_items_improved(details):
    """Improved function to handle bulk item adding with individual categories and eBay item IDs"""
    # Validate inputs
    if not isinstance(details, dict):
        raise ValueError("Invalid details format")
    
    if not isinstance(details.get('group'), str) or len(details.get('group', '')) > 50:
        raise ValueError("Invalid group ID")
    
    if not isinstance(details.get('storage', ''), str) or len(details.get('storage', '')) > 50:
        raise ValueError("Invalid storage")
    
    if not isinstance(details.get('list_date', ''), str) or len(details.get('list_date', '')) > 10:
        raise ValueError("Invalid list date")
    
    cur = mysql.connection.cursor()
    
    # Process items from the new form structure
    item_count = 0
    for key, value in details.items():
        if key.startswith("items-") and "-name" in key:
            # Extract item index from key like "items-0-name"
            item_index = key.split("-")[1]
            
            # Get item name
            item_name = value
            if not isinstance(item_name, str) or len(item_name) > 150 or not item_name.strip():
                continue  # Skip invalid items
            
            # Get category for this item
            category_key = f"items-{item_index}-category"
            category_id = details.get(category_key)
            if not isinstance(category_id, str) or len(category_id) > 36:
                continue  # Skip items without valid category
            
            # Get eBay item ID for this item (optional)
            ebay_item_key = f"items-{item_index}-ebay_item_id"
            ebay_item_id = details.get(ebay_item_key, '')
            if ebay_item_id:
                ebay_item_id = ebay_item_id.strip()
                if len(ebay_item_id) > 50:
                    ebay_item_id = ebay_item_id[:50]  # Truncate if too long
            else:
                ebay_item_id = None
            
            # Insert item with eBay item ID
            item_id = generate_uuid()
            cur.execute("""
                INSERT INTO items(id, name, group_id, category_id, storage, list_date, ebay_item_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (item_id, item_name, details['group'], category_id, details['storage'], details['list_date'], ebay_item_id))
            
            # Insert sale record
            cur.execute("INSERT INTO sale(id, price, shipping_fee, date) VALUES (%s, 0, 0, %s)",
                        (item_id, date.today().strftime("%Y-%m-%d")))
            
            item_count += 1
            print(f"DEBUG: Added item '{item_name}' with category '{category_id}' and eBay ID '{ebay_item_id}'")
    
    mysql.connection.commit()
    cur.close()
    
    print(f"DEBUG: Successfully added {item_count} items")
    return item_count

def set_quick_sale(details):
    # Validate inputs
    if not isinstance(details, dict):
        raise ValueError("Invalid details format")
    
    if not isinstance(details.get('name'), str) or len(details.get('name', '')) > 150:
        raise ValueError("Invalid item name")
    
    if not isinstance(details.get('group'), str) or len(details.get('group', '')) > 50:
        raise ValueError("Invalid group ID")
    
    if not isinstance(details.get('category'), str) or len(details.get('category', '')) > 36:
        raise ValueError("Invalid category ID")
    
    if not isinstance(details.get('list_date', ''), str) or len(details.get('list_date', '')) > 10:
        raise ValueError("Invalid list date")
    
    try:
        price = float(details.get('price', 0))
        if price < 0:
            raise ValueError("Price must be positive")
    except (ValueError, TypeError):
        raise ValueError("Invalid price")
    
    try:
        shipping_fee = float(details.get('shipping_fee', 0))
        if shipping_fee < 0:
            raise ValueError("Shipping fee must be positive")
    except (ValueError, TypeError):
        raise ValueError("Invalid shipping fee")
    
    item_id = generate_uuid()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO items(id, name, group_id, category_id, list_date, sold) VALUES (%s, %s, %s, %s, %s, 1)", 
                (item_id, details['name'], details['group'], details['category'], details['list_date']))
    cur.execute("INSERT INTO sale(id, price, shipping_fee, date) VALUES (%s, %s, %s, %s)",
                (item_id, price, shipping_fee, date.today().strftime("%Y-%m-%d")))
    mysql.connection.commit()
    cur.close()
    return item_id

def set_sale_data(details):
    # Validate critical inputs
    if not isinstance(details.get('id'), str) or len(details.get('id', '')) > 50:
        raise ValueError("Invalid item ID")
    
    try:
        price = float(details.get('price', 0))
        if price < 0:
            raise ValueError("Price must be positive")
    except (ValueError, TypeError):
        raise ValueError("Invalid price")
    
    try:
        shipping_fee = float(details.get('shipping_fee', 0))
        if shipping_fee < 0:
            raise ValueError("Shipping fee must be positive")
    except (ValueError, TypeError):
        raise ValueError("Invalid shipping fee")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE sale s
        INNER JOIN items i ON s.id = i.id
        INNER JOIN collection c ON i.group_id = c.id
        SET s.date = %s, s.price = %s, s.shipping_fee = %s 
        WHERE s.id = %s AND c.account = %s
    """, (details['sale_date'], price, shipping_fee, details['id'], session.get('id')))
    mysql.connection.commit()
    cur.close()


def set_items_modify(details):
    # Validate critical inputs
    if not isinstance(details.get('id'), str) or len(details.get('id', '')) > 50:
        raise ValueError("Invalid item ID")
    
    if not isinstance(details.get('name'), str) or len(details.get('name', '')) > 150:
        raise ValueError("Invalid item name")
    
    if not isinstance(details.get('group'), str) or len(details.get('group', '')) > 50:
        raise ValueError("Invalid group ID")
    
    if not isinstance(details.get('category'), str) or len(details.get('category', '')) > 36:
        raise ValueError("Invalid category ID")
    
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
    # Validate input
    if not isinstance(id, str) or len(id) > 50:
        raise ValueError("Invalid item ID")
    
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
    # Validate inputs
    if not isinstance(group_name, str) or len(group_name) > 200:
        raise ValueError("Invalid group name")
    
    try:
        price = float(details.get('price', 0))
        if price < 0:
            raise ValueError("Price must be positive")
    except (ValueError, TypeError):
        raise ValueError("Invalid price")
    
    if not isinstance(details.get('date'), str) or len(details.get('date', '')) > 10:
        raise ValueError("Invalid date")
    
    group_id = generate_uuid()
    cur = mysql.connection.cursor()
    
    # Get location data from details
    latitude = details.get('latitude', None)
    longitude = details.get('longitude', None)
    location_address = details.get('location_address', None)
    
    # Convert empty strings to None for database
    if latitude == '':
        latitude = None
    if longitude == '':
        longitude = None
    if location_address == '':
        location_address = None
    
    cur.execute("""
        INSERT INTO collection(id, name, date, price, image, account, group_id, latitude, longitude, location_address) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (group_id, group_name, details['date'], price, image_id, session.get('id'), 
          session.get('group_id'), latitude, longitude, location_address))
    mysql.connection.commit()
    cur.close()
    return group_id

def set_group_modify(details, image_id):
    # Validate inputs
    if not isinstance(details.get('id'), str) or len(details.get('id', '')) > 50:
        raise ValueError("Invalid group ID")
    
    if not isinstance(details.get('name'), str) or len(details.get('name', '')) > 200:
        raise ValueError("Invalid group name")
    
    try:
        price = float(details.get('price', 0))
        if price < 0:
            raise ValueError("Price must be positive")
    except (ValueError, TypeError):
        raise ValueError("Invalid price")
    
    if not isinstance(details.get('date'), str) or len(details.get('date', '')) > 10:
        raise ValueError("Invalid date")
    
    cur = mysql.connection.cursor()
    
    # Get location data from details
    latitude = details.get('latitude', None)
    longitude = details.get('longitude', None)
    location_address = details.get('location_address', None)
    
    # Convert empty strings to None for database
    if latitude == '':
        latitude = None
    if longitude == '':
        longitude = None
    if location_address == '':
        location_address = None
    
    cur.execute("""
        UPDATE collection 
        SET name = %s, date = %s, price = %s, image = %s, 
            latitude = %s, longitude = %s, location_address = %s 
        WHERE id = %s AND group_id = %s
    """, (details['name'], details['date'], price, image_id, 
          latitude, longitude, location_address,
          details['id'], session.get('group_id')))
    mysql.connection.commit()
    cur.close()

def remove_group_data(id):
    # Validate input
    if not isinstance(id, str) or len(id) > 50:
        raise ValueError("Invalid group ID")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        DELETE FROM collection 
        WHERE id = %s AND group_id = %s
    """, (id, session.get('group_id')))
    mysql.connection.commit()
    cur.close()





# Category Functions
def add_category(category_name, user_id):
    # Validate inputs
    if not isinstance(category_name, str) or len(category_name) > 50:
        raise ValueError("Invalid category name")
    
    if not isinstance(user_id, str) or len(user_id) > 50:
        raise ValueError("Invalid user ID")
    
    category_id = generate_uuid()
    cur = mysql.connection.cursor()
    # Get the next available id value
    cur.execute("SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM categories")
    next_id = cur.fetchone()['next_id']
    
    cur.execute("INSERT INTO categories (id, uuid_id, type, user_id) VALUES (%s, %s, %s, %s)", 
                (next_id, category_id, category_name, user_id))
    mysql.connection.commit()
    cur.close()
    return category_id

def update_category(category_id, category_name, user_id):
    # Validate inputs
    if not isinstance(category_id, str) or len(category_id) > 36:
        raise ValueError("Invalid category ID")
    
    if not isinstance(category_name, str) or len(category_name) > 50:
        raise ValueError("Invalid category name")
    
    if not isinstance(user_id, str) or len(user_id) > 50:
        raise ValueError("Invalid user ID")
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE categories SET type = %s WHERE uuid_id = %s AND user_id = %s",
                (category_name, category_id, user_id))
    mysql.connection.commit()
    cur.close()
    return True

def delete_category(category_id, user_id):
    # Validate inputs
    if not isinstance(category_id, str) or len(category_id) > 36:
        raise ValueError("Invalid category ID")
    
    if not isinstance(user_id, str) or len(user_id) > 50:
        raise ValueError("Invalid user ID")
    
    cur = mysql.connection.cursor()
    
    # Check if category is in use
    cur.execute("SELECT COUNT(*) as count FROM items WHERE category_id = %s", (category_id,))
    result = cur.fetchone()
    if result['count'] > 0:
        cur.close()
        return False, "Cannot delete category that has items assigned to it"
    
    # Delete the category
    cur.execute("DELETE FROM categories WHERE uuid_id = %s AND user_id = %s", (category_id, user_id))
    mysql.connection.commit()
    cur.close()
    return True, "Category deleted successfully"

# Admin Functions
def toggle_admin_status(user_id):
    # Validate input
    if not isinstance(user_id, str) or len(user_id) > 50:
        raise ValueError("Invalid user ID")
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE accounts SET is_admin = NOT is_admin WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()
    return True

def toggle_user_status(user_id):
    # Validate input
    if not isinstance(user_id, str) or len(user_id) > 50:
        raise ValueError("Invalid user ID")
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE accounts SET is_active = NOT is_active WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()
    return True

def deactivate_user(user_id):
    # Validate input
    if not isinstance(user_id, str) or len(user_id) > 50:
        raise ValueError("Invalid user ID")
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE accounts SET is_active = 0 WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()
    return True

def delete_user(user_id):
    """Delete a user account (keeping for backward compatibility)"""
    return deactivate_user(user_id)

def create_user(details):
    # Validate inputs
    if not isinstance(details, dict):
        raise ValueError("Invalid details format")
    
    if not isinstance(details.get('username'), str) or len(details.get('username', '')) > 100:
        raise ValueError("Invalid username")
    
    if not isinstance(details.get('email'), str) or len(details.get('email', '')) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(details.get('password'), str) or len(details.get('password', '')) < 6:
        raise ValueError("Invalid password")
    
    try:
        import bcrypt
        
        # Generate UUID for the new user
        user_id = generate_uuid()
        
        # Hash the password using bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(details['password'].encode('utf-8'), salt)
        
        # Set admin status (1 for admin, 0 for regular user)
        is_admin = details.get('is_admin', 0)
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO accounts(id, username, email, password, is_admin) VALUES (%s, %s, %s, %s, %s)", 
                    (user_id, details['username'], details['email'], hashed_password.decode('utf-8'), is_admin))
        mysql.connection.commit()
        cur.close()
        return user_id
    except Exception as e:
        print("Error creating user: {}".format(e))
        return None



def create_google_user(google_id, email, name, picture=None):
    # Validate inputs
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    if picture and (not isinstance(picture, str) or len(picture) > 500):
        raise ValueError("Invalid picture URL")
    
    try:
        # Generate UUID for the new user
        user_id = generate_uuid()
        
        cur = mysql.connection.cursor()
        
        # Try to insert without password first (if migration has been run)
        try:
            cur.execute("""
                INSERT INTO accounts(id, username, email, name, is_admin) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, email, email, name, 0))
        except Exception as e:
            # If that fails, the migration might not have been run
            # Try with a dummy password (this is a fallback)
            print("Warning: Google OAuth migration may not have been run. Using fallback method: {}".format(e))
            cur.execute("""
                INSERT INTO accounts(id, username, email, password, name, is_admin) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, email, email, 'google_oauth_user', name, 0))
        
        mysql.connection.commit()
        cur.close()
        return user_id
    except Exception as e:
        print("Error creating Google user: {}".format(e))
        return None

def create_user_from_admin(email, name):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    user_id = generate_uuid()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO accounts(id, username, email, password, is_admin) VALUES (%s, %s, %s, %s, %s)", 
                (user_id, name, email, 'admin_created', False))
    mysql.connection.commit()
    cur.close()
    return user_id

def link_google_account(user_id, google_id, name, picture=None):
    # Validate inputs
    if not isinstance(user_id, str) or len(user_id) > 50:
        raise ValueError("Invalid user ID")
    
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    if picture and (not isinstance(picture, str) or len(picture) > 500):
        raise ValueError("Invalid picture URL")
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE accounts SET google_id = %s, username = %s, picture = %s WHERE id = %s", 
                (google_id, name, picture, user_id))
    mysql.connection.commit()
    cur.close()
    return True

def add_group(name, description=""):
    # Validate inputs
    if not isinstance(name, str) or len(name) > 200:
        raise ValueError("Invalid group name")
    
    if not isinstance(description, str) or len(description) > 500:
        raise ValueError("Invalid description")
    
    group_id = generate_uuid()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO collection(id, name, date, price, account, group_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                (group_id, name, date.today().strftime("%Y-%m-%d"), 0, session.get('id'), session.get('group_id')))
    mysql.connection.commit()
    cur.close()
    return group_id

def record_access_attempt(email, google_id=None, name=None, picture=None, ip_address=None, user_agent=None):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if google_id and (not isinstance(google_id, str) or len(google_id) > 100):
        raise ValueError("Invalid Google ID")
    
    if name and (not isinstance(name, str) or len(name) > 100):
        raise ValueError("Invalid name")
    
    if picture and (not isinstance(picture, str) or len(picture) > 500):
        raise ValueError("Invalid picture URL")
    
    if ip_address and (not isinstance(ip_address, str) or len(ip_address) > 45):
        raise ValueError("Invalid IP address")
    
    if user_agent and (not isinstance(user_agent, str) or len(user_agent) > 500):
        raise ValueError("Invalid user agent")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO access_attempts (email, google_id, name, picture, ip_address, user_agent, attempt_time) 
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """, (email, google_id, name, picture, ip_address, user_agent))
    mysql.connection.commit()
    cur.close()
    return True

def get_pending_access_attempts():
    # No input parameters to validate for this function
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            a.id,
            a.email,
            a.name,
            a.google_id,
            a.picture,
            a.ip_address,
            a.user_agent,
            a.attempted_at as attempt_time,
            (SELECT COUNT(*) FROM access_attempts WHERE email = a.email) as total_requests,
            (SELECT COUNT(*) FROM access_attempts WHERE email = a.email AND status = 'denied') as denied_requests
        FROM access_attempts a
        WHERE a.status IS NULL OR a.status = 'pending'
        ORDER BY a.attempted_at DESC
    """)
    results = list(cur.fetchall())
    cur.close()
    return results

def update_access_attempt_status(attempt_id, status):
    # Validate inputs
    if not isinstance(attempt_id, str) or len(attempt_id) > 50:
        raise ValueError("Invalid attempt ID")
    
    if status not in ['approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE access_attempts SET status = %s WHERE id = %s", (status, attempt_id))
    mysql.connection.commit()
    cur.close()
    return True

def mark_item_returned(item_id, returned_fee):
    # Validate inputs
    if not isinstance(item_id, str) or len(item_id) > 50:
        raise ValueError("Invalid item ID")
    
    try:
        returned_fee = float(returned_fee)
        if returned_fee < 0:
            raise ValueError("Returned fee must be positive")
    except (ValueError, TypeError):
        raise ValueError("Invalid returned fee amount")
    
    cur = mysql.connection.cursor()
    try:
        # Mark item as returned (don't change sold status)
        cur.execute("""
            UPDATE items i
            INNER JOIN collection c ON i.group_id = c.id
            SET i.returned = 1
            WHERE i.id = %s AND c.account = %s
        """, (item_id, session.get('id')))
        
        # Update sale table with returned_fee
        cur.execute("""
            UPDATE sale s
            INNER JOIN items i ON s.id = i.id
            INNER JOIN collection c ON i.group_id = c.id
            SET s.returned_fee = %s
            WHERE s.id = %s AND c.account = %s
        """, (returned_fee, item_id, session.get('id')))
        
        mysql.connection.commit()
        return True
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cur.close()

def create_user_account(email, name, google_id=None, picture=None):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    if google_id and (not isinstance(google_id, str) or len(google_id) > 100):
        raise ValueError("Invalid Google ID")
    
    if picture and (not isinstance(picture, str) or len(picture) > 500):
        raise ValueError("Invalid picture URL")
    
    user_id = generate_uuid()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO accounts(id, username, email, password, is_admin) VALUES (%s, %s, %s, %s, %s)", 
                (user_id, name, email, 'google_oauth', False))
    mysql.connection.commit()
    cur.close()
    return user_id

def update_user_google_id(user_id, google_id):
    # Validate inputs
    if not isinstance(user_id, str) or len(user_id) > 50:
        raise ValueError("Invalid user ID")
    
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE accounts SET google_id = %s WHERE id = %s", (google_id, user_id))
    mysql.connection.commit()
    cur.close()
    return True

def get_access_attempts_by_email(email):
    # Validate input
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s 
        ORDER BY attempt_time DESC
    """, (email,))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_id(attempt_id):
    # Validate input
    if not isinstance(attempt_id, str) or len(attempt_id) > 50:
        raise ValueError("Invalid attempt ID")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE id = %s
    """, (attempt_id,))
    result = cur.fetchone()
    cur.close()
    return result

def get_access_attempts_by_status(status):
    # Validate input
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE status = %s 
        ORDER BY attempt_time DESC
    """, (status,))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_date_range(start_date, end_date):
    # Validate inputs
    if not isinstance(start_date, str) or len(start_date) > 10:
        raise ValueError("Invalid start date")
    
    if not isinstance(end_date, str) or len(end_date) > 10:
        raise ValueError("Invalid end date")
    
    # Validate date format
    try:
        datetime.datetime.strptime(start_date, '%Y-%m-%d')
        datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE DATE(attempt_time) BETWEEN %s AND %s 
        ORDER BY attempt_time DESC
    """, (start_date, end_date))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_ip(ip_address):
    # Validate input
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE ip_address = %s 
        ORDER BY attempt_time DESC
    """, (ip_address,))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_user_agent(user_agent):
    # Validate input
    if not isinstance(user_agent, str) or len(user_agent) > 500:
        raise ValueError("Invalid user agent")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE user_agent LIKE %s 
        ORDER BY attempt_time DESC
            """, ('%{}%'.format(user_agent),))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_google_id(google_id):
    # Validate input
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE google_id = %s 
        ORDER BY attempt_time DESC
    """, (google_id,))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_name(name):
    # Validate input
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE name LIKE %s 
        ORDER BY attempt_time DESC
            """, ('%{}%'.format(name),))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_email_and_status(email, status):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s AND status = %s 
        ORDER BY attempt_time DESC
    """, (email, status))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_ip_and_status(ip_address, status):
    # Validate inputs
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE ip_address = %s AND status = %s 
        ORDER BY attempt_time DESC
    """, (ip_address, status))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_google_id_and_status(google_id, status):
    # Validate inputs
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE google_id = %s AND status = %s 
        ORDER BY attempt_time DESC
    """, (google_id, status))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_name_and_status(name, status):
    # Validate inputs
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE name LIKE %s AND status = %s 
        ORDER BY attempt_time DESC
            """, ('%{}%'.format(name), status))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_email_and_ip(email, ip_address):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s AND ip_address = %s 
        ORDER BY attempt_time DESC
    """, (email, ip_address))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_email_and_google_id(email, google_id):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s AND google_id = %s 
        ORDER BY attempt_time DESC
    """, (email, google_id))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_email_and_name(email, name):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s AND name LIKE %s 
        ORDER BY attempt_time DESC
            """, (email, '%{}%'.format(name)))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_ip_and_google_id(ip_address, google_id):
    # Validate inputs
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE ip_address = %s AND google_id = %s 
        ORDER BY attempt_time DESC
    """, (ip_address, google_id))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_ip_and_name(ip_address, name):
    # Validate inputs
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE ip_address = %s AND name LIKE %s 
        ORDER BY attempt_time DESC
            """, (ip_address, '%{}%'.format(name)))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_google_id_and_name(google_id, name):
    # Validate inputs
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE google_id = %s AND name LIKE %s 
        ORDER BY attempt_time DESC
            """, (google_id, '%{}%'.format(name)))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_email_and_ip_and_status(email, ip_address, status):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s AND ip_address = %s AND status = %s 
        ORDER BY attempt_time DESC
    """, (email, ip_address, status))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_email_and_google_id_and_status(email, google_id, status):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s AND google_id = %s AND status = %s 
        ORDER BY attempt_time DESC
    """, (email, google_id, status))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_email_and_name_and_status(email, name, status):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s AND name LIKE %s AND status = %s 
        ORDER BY attempt_time DESC
            """, (email, '%{}%'.format(name), status))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_ip_and_google_id_and_status(ip_address, google_id, status):
    # Validate inputs
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE ip_address = %s AND google_id = %s AND status = %s 
        ORDER BY attempt_time DESC
    """, (ip_address, google_id, status))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_ip_and_name_and_status(ip_address, name, status):
    # Validate inputs
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE ip_address = %s AND name LIKE %s AND status = %s 
        ORDER BY attempt_time DESC
    """, (ip_address, '%{}%'.format(name), status))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_google_id_and_name_and_status(google_id, name, status):
    # Validate inputs
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE google_id = %s AND name LIKE %s AND status = %s 
        ORDER BY attempt_time DESC
    """, (google_id, '%{}%'.format(name), status))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_email_and_ip_and_google_id(email, ip_address, google_id):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s AND ip_address = %s AND google_id = %s 
        ORDER BY attempt_time DESC
    """, (email, ip_address, google_id))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_email_and_ip_and_name(email, ip_address, name):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s AND ip_address = %s AND name LIKE %s 
        ORDER BY attempt_time DESC
            """, (email, ip_address, '%{}%'.format(name)))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_email_and_ip_and_google_id_and_status(email, ip_address, google_id, status):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s AND ip_address = %s AND google_id = %s AND status = %s 
        ORDER BY attempt_time DESC
    """, (email, ip_address, google_id, status))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_email_and_ip_and_name_and_status(email, ip_address, name, status):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s AND ip_address = %s AND name LIKE %s AND status = %s 
        ORDER BY attempt_time DESC
            """, (email, ip_address, '%{}%'.format(name), status))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_ip_and_google_id_and_name_and_status(ip_address, google_id, name, status):
    # Validate inputs
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE ip_address = %s AND google_id = %s AND name LIKE %s AND status = %s 
        ORDER BY attempt_time DESC
            """, (ip_address, google_id, '%{}%'.format(name), status))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_email_and_ip_and_google_id_and_name(email, ip_address, google_id, name):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s AND ip_address = %s AND google_id = %s AND name LIKE %s 
        ORDER BY attempt_time DESC
            """, (email, ip_address, google_id, '%{}%'.format(name)))
    results = list(cur.fetchall())
    cur.close()
    return results

def get_access_attempts_by_email_and_ip_and_google_id_and_name_and_status(email, ip_address, google_id, name, status):
    # Validate inputs
    if not isinstance(email, str) or len(email) > 100:
        raise ValueError("Invalid email")
    
    if not isinstance(ip_address, str) or len(ip_address) > 45:
        raise ValueError("Invalid IP address")
    
    if not isinstance(google_id, str) or len(google_id) > 100:
        raise ValueError("Invalid Google ID")
    
    if not isinstance(name, str) or len(name) > 100:
        raise ValueError("Invalid name")
    
    if not isinstance(status, str) or status not in ['pending', 'approved', 'denied']:
        raise ValueError("Invalid status")
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            email,
            name,
            google_id,
            picture,
            ip_address,
            user_agent,
            attempt_time,
            status
        FROM access_attempts 
        WHERE email = %s AND ip_address = %s AND google_id = %s AND name LIKE %s AND status = %s 
        ORDER BY attempt_time DESC
            """, (email, ip_address, google_id, '%{}%'.format(name), status))
    results = list(cur.fetchall())
    cur.close()
    return results

# Group Management Functions
def create_group(name, description=None):
    """Create a new group"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO `groups` (name, description) 
            VALUES (%s, %s)
        """, (name, description))
        mysql.connection.commit()
        group_id = cur.lastrowid
        cur.close()
        return group_id
    except Exception as e:
        print("Error creating group: {}".format(e))
        return None

def update_group(group_id, name=None, description=None):
    """Update group information"""
    try:
        cur = mysql.connection.cursor()
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = %s")
            params.append(name)
        
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        
        if updates:
            params.append(group_id)
            cur.execute(f"""
                UPDATE `groups` 
                SET {', '.join(updates)}
                WHERE id = %s
            """, params)
            mysql.connection.commit()
        
        cur.close()
        return True
    except Exception as e:
        print("Error updating group: {}".format(e))
        return False

def move_user_to_group(user_id, group_id):
    """Move a user to a different group"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE accounts 
            SET group_id = %s 
            WHERE id = %s
        """, (group_id, user_id))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print("Error moving user to group: {}".format(e))
        return False

def delete_group(group_id):
    """Delete a collection and all its associated items (not the user group)"""
    try:
        cur = mysql.connection.cursor()
        
        # Delete all items in the collection
        cur.execute("DELETE FROM items WHERE group_id = %s", (group_id,))
        
        # Delete all sales for items in the collection
        cur.execute("""
            DELETE s FROM sale s 
            INNER JOIN items i ON s.id = i.id 
            WHERE i.group_id = %s
        """, (group_id,))
        
        # Delete the collection record
        cur.execute("DELETE FROM collection WHERE id = %s", (group_id,))
        
        mysql.connection.commit()
        cur.close()
        return True, "Collection and all associated items deleted successfully"
    except Exception as e:
        print("Error deleting collection: {}".format(e))
        return False, str(e)