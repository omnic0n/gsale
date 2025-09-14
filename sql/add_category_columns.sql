-- Add required columns to categories table
-- This is the minimal migration needed

-- Add uuid_id column if it doesn't exist
ALTER TABLE `categories` ADD COLUMN `uuid_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL AFTER `id`;

-- Add user_id column if it doesn't exist  
ALTER TABLE `categories` ADD COLUMN `user_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL AFTER `uuid_id`;

-- Generate UUIDs for existing categories that don't have them
UPDATE `categories` SET `uuid_id` = UUID() WHERE `uuid_id` IS NULL;

-- Add indexes
ALTER TABLE `categories` ADD INDEX `idx_categories_uuid_id` (`uuid_id`);
ALTER TABLE `categories` ADD INDEX `idx_categories_user_id` (`user_id`);
