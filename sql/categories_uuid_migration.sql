-- Migration to update categories table to support UUIDs
-- Run this script to update your existing database

-- First, add a new column for UUID-based IDs
ALTER TABLE `categories` ADD COLUMN `uuid_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL AFTER `id`;

-- Add user_id column for user-specific categories
ALTER TABLE `categories` ADD COLUMN `user_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL AFTER `uuid_id`;

-- Generate UUIDs for existing categories
UPDATE `categories` SET `uuid_id` = UUID() WHERE `uuid_id` IS NULL;

-- Make uuid_id the primary key (we'll need to drop the old primary key first)
ALTER TABLE `categories` DROP PRIMARY KEY;

-- Add new primary key on uuid_id
ALTER TABLE `categories` ADD PRIMARY KEY (`uuid_id`);

-- Add index for user_id
ALTER TABLE `categories` ADD INDEX `idx_categories_user_id` (`user_id`);

-- Add foreign key constraint for user_id (if accounts table exists)
-- ALTER TABLE `categories` ADD CONSTRAINT `fk_categories_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts`(`id`) ON DELETE CASCADE;

-- Note: The old `id` column is kept for backward compatibility but is no longer the primary key
-- You may want to drop it later after ensuring all code uses uuid_id
