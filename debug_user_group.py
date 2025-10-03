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
            print(f"User ID: {user_info['id']}")
            print(f"Username: {user_info['username']}")
            print(f"Email: {user_info['email']}")
            print(f"Group ID: {user_info['group_id']}")
            print(f"Group Name: {user_info['group_name']}")
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
        print(f"Found {len(collections)} collections for group {user_info['group_id']}")
        for col in collections:
            print(f"  - {col['name']} (ID: {col['id']}, Account: {col['account']})")
        
        # Check if there are any collections with the user's account
        print("\n=== COLLECTIONS FOR USER'S ACCOUNT ===")
        cur.execute("""
            SELECT id, name, group_id, account
            FROM collection
            WHERE account = %s
            LIMIT 5
        """, (user_info['id'],))
        user_collections = cur.fetchall()
        print(f"Found {len(user_collections)} collections for user account {user_info['id']}")
        for col in user_collections:
            print(f"  - {col['name']} (ID: {col['id']}, Group ID: {col['group_id']})")
        
        cur.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_user_group()
