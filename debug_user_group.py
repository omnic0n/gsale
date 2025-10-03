#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from flask_mysqldb import MySQL

# Initialize MySQL
mysql = MySQL(app)

def debug_user_group():
    """Debug the user's group assignment"""
    try:
        cur = mysql.connection.cursor()
        
        # Check the user's account info
        print("=== USER ACCOUNT INFO ===")
        cur.execute("""
            SELECT a.id, a.username, a.email, a.group_id, g.name as group_name
            FROM accounts a
            LEFT JOIN `groups` g ON a.group_id = g.id
            WHERE a.email = 'ethanmaorfrisco@gmail.com'
        """)
        user_info = cur.fetchone()
        if user_info:
            print("User ID: {}".format(user_info['id']))
            print("Username: {}".format(user_info['username']))
            print("Email: {}".format(user_info['email']))
            print("Group ID: {}".format(user_info['group_id']))
            print("Group Name: {}".format(user_info['group_name']))
        else:
            print("❌ User not found!")
            return
        
        # Check collections for this group
        print("\n=== COLLECTIONS FOR THIS GROUP ===")
        cur.execute("""
            SELECT id, name, group_id, account
            FROM collection
            WHERE group_id = %s
            LIMIT 5
        """, (user_info['group_id'],))
        collections = cur.fetchall()
        print("Found {} collections for group {}".format(len(collections), user_info['group_id']))
        for col in collections:
            print("  - {} (ID: {}, Account: {})".format(col['name'], col['id'], col['account']))
        
        # Check if there are any collections with the user's account
        print("\n=== COLLECTIONS FOR USER'S ACCOUNT ===")
        cur.execute("""
            SELECT id, name, group_id, account
            FROM collection
            WHERE account = %s
            LIMIT 5
        """, (user_info['id'],))
        user_collections = cur.fetchall()
        print("Found {} collections for user account {}".format(len(user_collections), user_info['id']))
        for col in user_collections:
            print("  - {} (ID: {}, Group ID: {})".format(col['name'], col['id'], col['group_id']))
        
        cur.close()
        
    except Exception as e:
        print("Error: {}".format(e))

if __name__ == "__main__":
    debug_user_group()
