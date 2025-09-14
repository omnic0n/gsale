-- Fix categories table id column to be auto-increment
-- This resolves the "Field 'id' doesn't have a default value" error

-- First, add uuid_id column if it doesn't exist
ALTER TABLE `categories` ADD COLUMN `uuid_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL AFTER `id`;

-- Add user_id column if it doesn't exist  
ALTER TABLE `categories` ADD COLUMN `user_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL AFTER `uuid_id`;

-- Generate UUIDs for existing categories that don't have them
UPDATE `categories` SET `uuid_id` = UUID() WHERE `uuid_id` IS NULL;

-- Check if id column is already auto-increment, if not make it auto-increment
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

-- Add indexes
ALTER TABLE `categories` ADD INDEX `idx_categories_uuid_id` (`uuid_id`);
ALTER TABLE `categories` ADD INDEX `idx_categories_user_id` (`user_id`);
