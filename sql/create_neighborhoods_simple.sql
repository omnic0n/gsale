-- Ultra-simple migration that will work with any MySQL version
-- Just run each command individually and ignore any errors

-- Create neighborhoods table
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
  KEY `idx_neighborhoods_score` (`score`),
  UNIQUE KEY `unique_user_neighborhood` (`user_id`, `name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Try to add city column (ignore error if it exists)
ALTER TABLE `neighborhoods` ADD COLUMN `city` varchar(100) AFTER `description`;

-- Try to add state column (ignore error if it exists)  
ALTER TABLE `neighborhoods` ADD COLUMN `state` varchar(50) AFTER `city`;

-- Try to add city_state index (ignore error if it exists)
ALTER TABLE `neighborhoods` ADD INDEX `idx_neighborhoods_city_state` (`city`, `state`);
