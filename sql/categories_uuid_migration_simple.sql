-- Simple migration to update categories table to support UUIDs
-- This script handles the transition more gracefully

-- First, let's check the current structure and add the uuid_id column if it doesn't exist
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

-- Make the old id column auto-increment to handle the constraint
ALTER TABLE `categories` MODIFY COLUMN `id` mediumint NOT NULL AUTO_INCREMENT;

-- Add index for uuid_id if it doesn't exist
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

-- Add index for user_id if it doesn't exist
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

-- Note: We keep the old id column as auto-increment to satisfy the constraint
-- The uuid_id column is used for the actual category identification in the application
