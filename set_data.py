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





# Category Functions
def add_category(category_name, user_id):
    """Add a new category"""
    cur = mysql.connection.cursor()
    try:
        import uuid
        category_id = str(uuid.uuid4())
        cur.execute("INSERT INTO categories (id, type, user_id) VALUES (%s, %s, %s)", (category_id, category_name, user_id))
        mysql.connection.commit()
        return category_id
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error adding category: {e}")
        return None
    finally:
        cur.close()

def update_category(category_id, category_name, user_id):
    """Update a category"""
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE categories SET type = %s WHERE id = %s AND user_id = %s", 
                   (category_name, category_id, user_id))
        mysql.connection.commit()
        return cur.rowcount > 0
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error updating category: {e}")
        return False
    finally:
        cur.close()

def delete_category(category_id, user_id):
    """Delete a category and update all items to be Uncategorized"""
    cur = mysql.connection.cursor()
    try:
        # Check if category is used by any items
        cur.execute("SELECT COUNT(*) as count FROM items WHERE category_id = %s", (category_id,))
        result = cur.fetchone()
        affected_items = result['count']
        
        if affected_items > 0:
            # Find the user's Uncategorized category
            cur.execute("SELECT id FROM categories WHERE type = 'Uncategorized' AND user_id = %s", (user_id,))
            uncategorized_result = cur.fetchone()
            
            if uncategorized_result:
                uncategorized_id = uncategorized_result['id']
                # Update all items to be Uncategorized
                cur.execute("UPDATE items SET category_id = %s WHERE category_id = %s", (uncategorized_id, category_id))
                updated_items = cur.rowcount
                
                # Delete the category (only if it belongs to the user)
                cur.execute("DELETE FROM categories WHERE id = %s AND user_id = %s", (category_id, user_id))
                mysql.connection.commit()
                
                return True, f"Category deleted successfully. {updated_items} items have been moved to Uncategorized."
            else:
                # If no Uncategorized category exists, create one
                import uuid
                uncategorized_id = str(uuid.uuid4())
                cur.execute("INSERT INTO categories (id, type, user_id) VALUES (%s, %s, %s)", 
                           (uncategorized_id, 'Uncategorized', user_id))
                
                # Update all items to be Uncategorized
                cur.execute("UPDATE items SET category_id = %s WHERE category_id = %s", (uncategorized_id, category_id))
                updated_items = cur.rowcount
                
                # Delete the category (only if it belongs to the user)
                cur.execute("DELETE FROM categories WHERE id = %s AND user_id = %s", (category_id, user_id))
                mysql.connection.commit()
                
                return True, f"Category deleted successfully. {updated_items} items have been moved to Uncategorized."
        else:
            # No items using this category, just delete it
            cur.execute("DELETE FROM categories WHERE id = %s AND user_id = %s", (category_id, user_id))
            mysql.connection.commit()
            return True, "Category deleted successfully"
            
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error deleting category: {e}")
        return False, f"Error deleting category: {e}"
    finally:
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
        # Check if MySQL connection is available
        if not mysql or not hasattr(mysql, 'connection') or not mysql.connection:
            return False
            
        # Test connection
        try:
            mysql.connection.ping(reconnect=True)
        except Exception:
            return False
            
        cur = mysql.connection.cursor()
        
        # First, get all the group IDs for this user
        cur.execute("SELECT id FROM collection WHERE account = %s", (user_id,))
        group_ids = [row[0] for row in cur.fetchall()]
        
        if group_ids:
            # Delete sales for items in these groups
            if len(group_ids) == 1:
                cur.execute("DELETE s FROM sale s INNER JOIN items i ON s.id = i.id WHERE i.group_id = %s", (group_ids[0],))
            else:
                cur.execute("DELETE s FROM sale s INNER JOIN items i ON s.id = i.id WHERE i.group_id IN %s", (tuple(group_ids),))
            
            # Delete items in these groups
            if len(group_ids) == 1:
                cur.execute("DELETE FROM items WHERE group_id = %s", (group_ids[0],))
            else:
                cur.execute("DELETE FROM items WHERE group_id IN %s", (tuple(group_ids),))
            
            # Delete the collections
            cur.execute("DELETE FROM collection WHERE account = %s", (user_id,))
        
        # Delete cases for this user (if table exists)
        try:
            cur.execute("DELETE FROM cases WHERE account = %s", (user_id,))
        except Exception:
            # Continue with deletion even if cases table doesn't exist
            pass
        
        # Delete expenses for this user (if table exists)
        try:
            cur.execute("DELETE FROM expenses WHERE account = %s", (user_id,))
        except Exception:
            # Continue with deletion even if expenses table doesn't exist
            pass
        
        # Finally delete the user account
        cur.execute("DELETE FROM accounts WHERE id = %s", (user_id,))
        
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error deleting user {user_id}: {e}")
        # Rollback on error
        try:
            mysql.connection.rollback()
        except Exception:
            pass
        return False

def create_user(details):
    """Create a new user account"""
    try:
        import bcrypt
        
        # Generate UUID for the new user
        user_id = generate_uuid()
        
        # Hash the password using bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(details['password'].encode('utf-8'), salt)
        
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

def change_user_password(user_id, new_password):
    """Change a user's password"""
    try:
        import bcrypt
        
        # Hash the new password using bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE accounts SET password = %s WHERE id = %s", (hashed_password, user_id))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error changing password: {e}")
        return False

def create_google_user(google_id, email, name, picture=None):
    """Create a new user account via Google OAuth"""
    try:
        # Generate UUID for the new user
        user_id = generate_uuid()
        
        cur = mysql.connection.cursor()
        
        # Try to insert without password first (if migration has been run)
        try:
            cur.execute("""
                INSERT INTO accounts(id, username, email, google_id, name, picture, is_admin) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, email, email, google_id, name, picture, 0))
        except Exception as e:
            # If that fails, the migration might not have been run
            # Try with a dummy password (this is a fallback)
            print(f"Warning: Google OAuth migration may not have been run. Using fallback method: {e}")
            cur.execute("""
                INSERT INTO accounts(id, username, email, password, google_id, name, picture, is_admin) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, email, email, 'google_oauth_user', google_id, name, picture, 0))
        
        mysql.connection.commit()
        cur.close()
        return user_id
    except Exception as e:
        print(f"Error creating Google user: {e}")
        return None

def link_google_account(user_id, google_id, name, picture=None):
    """Link a Google account to an existing user"""
    try:
        cur = mysql.connection.cursor()
        
        # Update the existing user with Google OAuth information
        cur.execute("""
            UPDATE accounts 
            SET google_id = %s, name = %s, picture = %s 
            WHERE id = %s
        """, (google_id, name, picture, user_id))
        
        mysql.connection.commit()
        cur.close()
        return user_id
    except Exception as e:
        print(f"Error linking Google account: {e}")
        return None

def add_group(name, description=""):
    """Add a new group"""
    try:
        group_id = generate_uuid()
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO collection(id, name, description, date, price, account) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (group_id, name, description, datetime.now().date(), 0.00, session.get('id')))
        mysql.connection.commit()
        cur.close()
        return group_id
    except Exception as e:
        print(f"Error adding group: {e}")
        return None