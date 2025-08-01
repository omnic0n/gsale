-- Add is_active column to accounts table
ALTER TABLE `accounts` ADD COLUMN `is_active` TINYINT(1) DEFAULT 1 AFTER `is_admin`;

-- Update existing users to be active
UPDATE `accounts` SET `is_active` = 1 WHERE `is_active` IS NULL; 