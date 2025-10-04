-- Rollback script for group system migration
-- Use this if you need to revert back to the original user-based system

-- Step 1: Drop the new tables and functions
DROP TABLE IF EXISTS `group_members`;
DROP FUNCTION IF EXISTS `get_group_stats`;
DROP PROCEDURE IF EXISTS `move_user_to_group`;
DROP PROCEDURE IF EXISTS `create_group_with_user`;

-- Step 2: Remove group_id columns from all tables
ALTER TABLE `accounts` DROP COLUMN IF EXISTS `group_id`;
ALTER TABLE `collection` DROP COLUMN IF EXISTS `group_id`;
ALTER TABLE `expenses` DROP COLUMN IF EXISTS `group_id`;
ALTER TABLE `cases` DROP COLUMN IF EXISTS `group_id`;
ALTER TABLE `categories` DROP COLUMN IF EXISTS `group_id`;

-- Step 3: Drop the groups table
DROP TABLE IF EXISTS `groups`;

-- Step 4: Restore from backup tables (if they exist)
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'accounts_backup') > 0,
    'TRUNCATE TABLE `accounts`; INSERT INTO `accounts` SELECT * FROM `accounts_backup`',
    'SELECT "accounts_backup table does not exist" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'collection_backup') > 0,
    'TRUNCATE TABLE `collection`; INSERT INTO `collection` SELECT * FROM `collection_backup`',
    'SELECT "collection_backup table does not exist" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'expenses_backup') > 0,
    'TRUNCATE TABLE `expenses`; INSERT INTO `expenses` SELECT * FROM `expenses_backup`',
    'SELECT "expenses_backup table does not exist" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'cases_backup') > 0,
    'TRUNCATE TABLE `cases`; INSERT INTO `cases` SELECT * FROM `cases_backup`',
    'SELECT "cases_backup table does not exist" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'categories_backup') > 0,
    'TRUNCATE TABLE `categories`; INSERT INTO `categories` SELECT * FROM `categories_backup`',
    'SELECT "categories_backup table does not exist" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Step 5: Clean up backup tables (optional)
-- Uncomment the following lines if you want to remove backup tables after rollback
-- DROP TABLE IF EXISTS `accounts_backup`;
-- DROP TABLE IF EXISTS `collection_backup`;
-- DROP TABLE IF EXISTS `expenses_backup`;
-- DROP TABLE IF EXISTS `cases_backup`;
-- DROP TABLE IF EXISTS `categories_backup`;

SELECT 'Rollback completed successfully!' as status;
