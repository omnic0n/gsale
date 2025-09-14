-- Fix the id column to have a default value
-- This resolves the "Field 'id' doesn't have a default value" error

-- First, let's see the current structure
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    EXTRA
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
AND TABLE_NAME = 'categories'
AND COLUMN_NAME = 'id';

-- Add uuid_id column if it doesn't exist
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'categories' 
     AND COLUMN_NAME = 'uuid_id') = 0,
    'ALTER TABLE `categories` ADD COLUMN `uuid_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL AFTER `id`',
    'SELECT "uuid_id column already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add user_id column if it doesn't exist  
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'categories' 
     AND COLUMN_NAME = 'user_id') = 0,
    'ALTER TABLE `categories` ADD COLUMN `user_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL AFTER `uuid_id`',
    'SELECT "user_id column already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Generate UUIDs for existing categories that don't have them
UPDATE `categories` SET `uuid_id` = UUID() WHERE `uuid_id` IS NULL;

-- Make the id column auto-increment (this will give it a default value)
-- First check if it's already auto-increment
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'categories' 
     AND COLUMN_NAME = 'id' 
     AND EXTRA LIKE '%auto_increment%') = 0,
    'ALTER TABLE `categories` MODIFY COLUMN `id` mediumint NOT NULL AUTO_INCREMENT',
    'SELECT "id column is already auto-increment" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add indexes if they don't exist
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'categories' 
     AND INDEX_NAME = 'idx_categories_uuid_id') = 0,
    'ALTER TABLE `categories` ADD INDEX `idx_categories_uuid_id` (`uuid_id`)',
    'SELECT "uuid_id index already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'categories' 
     AND INDEX_NAME = 'idx_categories_user_id') = 0,
    'ALTER TABLE `categories` ADD INDEX `idx_categories_user_id` (`user_id`)',
    'SELECT "user_id index already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
