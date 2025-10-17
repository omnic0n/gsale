-- Remove score system and add neighborhood assignment to collections
-- This allows tagging group sales to specific neighborhoods

-- Remove score column from neighborhoods table
ALTER TABLE `neighborhoods` DROP COLUMN IF EXISTS `score`;

-- Ensure neighborhood_id column exists in collection table
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'collection' 
     AND COLUMN_NAME = 'neighborhood_id') = 0,
    'ALTER TABLE `collection` ADD COLUMN `neighborhood_id` varchar(36) NULL AFTER `account`',
    'SELECT "Column neighborhood_id already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add index for neighborhood_id in collection table if it doesn't exist
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'collection' 
     AND INDEX_NAME = 'idx_collection_neighborhood_id') = 0,
    'ALTER TABLE `collection` ADD INDEX `idx_collection_neighborhood_id` (`neighborhood_id`)',
    'SELECT "Index idx_collection_neighborhood_id already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add composite index for neighborhood-based queries if it doesn't exist
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'collection' 
     AND INDEX_NAME = 'idx_collection_neighborhood_date') = 0,
    'ALTER TABLE `collection` ADD INDEX `idx_collection_neighborhood_date` (`neighborhood_id`, `date`)',
    'SELECT "Index idx_collection_neighborhood_date already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
