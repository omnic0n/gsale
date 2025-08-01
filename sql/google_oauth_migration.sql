-- Migration to add Google OAuth support to accounts table
-- Run this script to update your existing database

-- Make password field nullable for Google OAuth users
ALTER TABLE `accounts` MODIFY COLUMN `password` varchar(255) NULL;

-- Add Google OAuth columns to accounts table
ALTER TABLE `accounts` 
ADD COLUMN `google_id` varchar(100) DEFAULT NULL AFTER `email`,
ADD COLUMN `name` varchar(100) DEFAULT NULL AFTER `google_id`,
ADD COLUMN `picture` varchar(500) DEFAULT NULL AFTER `name`,
ADD COLUMN `is_admin` tinyint(1) DEFAULT 0 AFTER `picture`,
ADD COLUMN `created_at` timestamp DEFAULT CURRENT_TIMESTAMP AFTER `is_admin`;

-- Add unique index for google_id
ALTER TABLE `accounts` ADD UNIQUE KEY `google_id` (`google_id`);

-- Add index for is_admin
ALTER TABLE `accounts` ADD INDEX `idx_accounts_is_admin` (`is_admin`);

-- Add index for created_at
ALTER TABLE `accounts` ADD INDEX `idx_accounts_created_at` (`created_at`);

-- Update existing accounts to have is_admin = 0 if not set
UPDATE `accounts` SET `is_admin` = 0 WHERE `is_admin` IS NULL; 