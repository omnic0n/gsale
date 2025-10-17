-- Minimal migration: Only add what's missing
-- This script will only add the neighborhoods table and any missing columns/indexes

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

-- Add city and state columns to neighborhoods table if they don't exist
ALTER TABLE `neighborhoods` 
ADD COLUMN IF NOT EXISTS `city` varchar(100) AFTER `description`,
ADD COLUMN IF NOT EXISTS `state` varchar(50) AFTER `city`;

-- Add indexes for city and state if they don't exist
ALTER TABLE `neighborhoods` 
ADD INDEX IF NOT EXISTS `idx_neighborhoods_city_state` (`city`, `state`);
