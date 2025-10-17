-- Simple migration script compatible with older MySQL versions
-- This will create the neighborhoods table and add missing columns safely

-- Create neighborhoods table (will be skipped if it already exists)
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

-- Add city column if it doesn't exist (using error handling)
SET @sql = 'ALTER TABLE `neighborhoods` ADD COLUMN `city` varchar(100) AFTER `description`';
SET @sql = IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'neighborhoods' 
     AND COLUMN_NAME = 'city') = 0,
    @sql,
    'SELECT "Column city already exists" as message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add state column if it doesn't exist (using error handling)
SET @sql = 'ALTER TABLE `neighborhoods` ADD COLUMN `state` varchar(50) AFTER `city`';
SET @sql = IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'neighborhoods' 
     AND COLUMN_NAME = 'state') = 0,
    @sql,
    'SELECT "Column state already exists" as message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add city_state index if it doesn't exist
SET @sql = 'ALTER TABLE `neighborhoods` ADD INDEX `idx_neighborhoods_city_state` (`city`, `state`)';
SET @sql = IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'neighborhoods' 
     AND INDEX_NAME = 'idx_neighborhoods_city_state') = 0,
    @sql,
    'SELECT "Index idx_neighborhoods_city_state already exists" as message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
