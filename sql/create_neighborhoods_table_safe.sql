-- Create neighborhoods table for managing neighborhood scoring system
-- This allows users to create and manage neighborhoods with sales-based scoring

CREATE TABLE IF NOT EXISTS `neighborhoods` (
  `id` varchar(36) NOT NULL DEFAULT (uuid()),
  `name` varchar(100) NOT NULL,
  `description` text,
  `city` varchar(100),
  `state` varchar(50),
  `score` int NOT NULL DEFAULT 5,
  `user_id` varchar(36) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_neighborhoods_user_id` (`user_id`),
  KEY `idx_neighborhoods_name` (`name`),
  KEY `idx_neighborhoods_city_state` (`city`, `state`),
  KEY `idx_neighborhoods_score` (`score`),
  UNIQUE KEY `unique_user_neighborhood` (`user_id`, `name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Add neighborhood_id column to collection table to link purchases to neighborhoods
-- Only add if it doesn't already exist
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

-- Add index for neighborhood_id in collection table
-- Only add if it doesn't already exist
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

-- Add composite index for neighborhood-based queries
-- Only add if it doesn't already exist
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
