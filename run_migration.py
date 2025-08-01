#!/usr/bin/env python3
"""
Script to run the Google OAuth migration
"""

import mysql.connector
from mysql.connector import Error

def run_migration():
    """Run the Google OAuth migration"""
    connection = None
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='gsale',
            password='KMFJfsbx2iAQttV',
            database='gsale'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Migration SQL commands
            migration_commands = [
                # Make password field nullable for Google OAuth users
                "ALTER TABLE `accounts` MODIFY COLUMN `password` varchar(255) NULL",
                
                # Add Google OAuth columns to accounts table
                "ALTER TABLE `accounts` ADD COLUMN `google_id` varchar(100) DEFAULT NULL AFTER `email`",
                "ALTER TABLE `accounts` ADD COLUMN `name` varchar(100) DEFAULT NULL AFTER `google_id`",
                "ALTER TABLE `accounts` ADD COLUMN `picture` varchar(500) DEFAULT NULL AFTER `name`",
                "ALTER TABLE `accounts` ADD COLUMN `is_admin` tinyint(1) DEFAULT 0 AFTER `picture`",
                "ALTER TABLE `accounts` ADD COLUMN `created_at` timestamp DEFAULT CURRENT_TIMESTAMP AFTER `is_admin`",
                
                # Add unique index for google_id
                "ALTER TABLE `accounts` ADD UNIQUE KEY `google_id` (`google_id`)",
                
                # Add index for is_admin
                "ALTER TABLE `accounts` ADD INDEX `idx_accounts_is_admin` (`is_admin`)",
                
                # Add index for created_at
                "ALTER TABLE `accounts` ADD INDEX `idx_accounts_created_at` (`created_at`)",
                
                # Update existing accounts to have is_admin = 0 if not set
                "UPDATE `accounts` SET `is_admin` = 0 WHERE `is_admin` IS NULL"
            ]
            
            print("Starting Google OAuth migration...")
            
            for i, command in enumerate(migration_commands, 1):
                try:
                    print(f"Executing command {i}/{len(migration_commands)}: {command[:50]}...")
                    cursor.execute(command)
                    print(f"✓ Command {i} completed successfully")
                except Error as e:
                    if "Duplicate key name" in str(e) or "Duplicate column name" in str(e):
                        print(f"⚠ Command {i} skipped (already exists): {e}")
                    else:
                        print(f"✗ Command {i} failed: {e}")
                        raise
            
            # Commit the changes
            connection.commit()
            print("✓ Migration completed successfully!")
            
    except Error as e:
        print(f"Error during migration: {e}")
        if "Can't connect to MySQL server" in str(e):
            print("\nMySQL server is not running or not accessible.")
            print("Please make sure MySQL is running and try again.")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")
    
    return True

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\nMigration completed! You can now use Google OAuth login.")
    else:
        print("\nMigration failed. Please check the error messages above.") 