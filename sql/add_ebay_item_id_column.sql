-- Add ebay_item_id column to items table
-- This migration adds an optional eBay item ID field to link items with eBay listings

-- Add ebay_item_id column if it doesn't exist
ALTER TABLE `items` ADD COLUMN `ebay_item_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL AFTER `list_date`;

-- Add index for ebay_item_id for better query performance
ALTER TABLE `items` ADD INDEX `idx_items_ebay_item_id` (`ebay_item_id`);

-- Add composite index for common queries involving eBay items
ALTER TABLE `items` ADD INDEX `idx_items_ebay_sold` (`ebay_item_id`, `sold`);
