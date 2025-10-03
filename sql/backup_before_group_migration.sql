-- Backup script before group system migration
-- Run this before executing group_system_migration.sql

-- Create backup tables
CREATE TABLE IF NOT EXISTS `accounts_backup` AS SELECT * FROM `accounts`;
CREATE TABLE IF NOT EXISTS `collection_backup` AS SELECT * FROM `collection`;
CREATE TABLE IF NOT EXISTS `expenses_backup` AS SELECT * FROM `expenses`;
CREATE TABLE IF NOT EXISTS `cases_backup` AS SELECT * FROM `cases`;

-- Backup categories table if it exists
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'categories') > 0,
    'CREATE TABLE IF NOT EXISTS `categories_backup` AS SELECT * FROM `categories`',
    'SELECT "categories table does not exist" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Show backup status
SELECT 'Backup completed successfully!' as status;
SELECT 
    'accounts_backup' as table_name,
    COUNT(*) as record_count
FROM `accounts_backup`
UNION ALL
SELECT 
    'collection_backup' as table_name,
    COUNT(*) as record_count
FROM `collection_backup`
UNION ALL
SELECT 
    'expenses_backup' as table_name,
    COUNT(*) as record_count
FROM `expenses_backup`
UNION ALL
SELECT 
    'cases_backup' as table_name,
    COUNT(*) as record_count
FROM `cases_backup`;
