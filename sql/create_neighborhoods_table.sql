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
ALTER TABLE `collection` ADD COLUMN `neighborhood_id` varchar(36) NULL AFTER `account`;

-- Add index for neighborhood_id in collection table
ALTER TABLE `collection` ADD INDEX `idx_collection_neighborhood_id` (`neighborhood_id`);

-- Add composite index for neighborhood-based queries
ALTER TABLE `collection` ADD INDEX `idx_collection_neighborhood_date` (`neighborhood_id`, `date`);
