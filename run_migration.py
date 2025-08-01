#!/usr/bin/env python3
"""
Database migration script to add location columns to collection table
"""

import mysql.connector
from mysql.connector import Error

def run_migration():
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            user='gsale',
            password='KMFJfsbx2iAQttV',
            database='gsale'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Check if columns already exist
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'gsale' 
                AND TABLE_NAME = 'collection' 
                AND COLUMN_NAME IN ('latitude', 'longitude', 'location_name', 'location_address')
            """)
            
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            if not existing_columns:
                print("Adding location columns to collection table...")
                
                # Add location columns
                migration_sql = """
                ALTER TABLE collection 
                ADD COLUMN latitude DECIMAL(10, 8) NULL,
                ADD COLUMN longitude DECIMAL(11, 8) NULL,
                ADD COLUMN location_name VARCHAR(255) NULL,
                ADD COLUMN location_address TEXT NULL
                """
                
                cursor.execute(migration_sql)
                
                # Add indexes
                print("Adding indexes...")
                cursor.execute("CREATE INDEX idx_collection_location ON collection(latitude, longitude)")
                cursor.execute("CREATE INDEX idx_collection_location_name ON collection(location_name)")
                
                connection.commit()
                print("✅ Migration completed successfully!")
                
            else:
                print(f"✅ Location columns already exist: {existing_columns}")
                
    except Error as e:
        print(f"❌ Error during migration: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    run_migration() 