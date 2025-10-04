-- Group System Migration Script
-- This script converts the individual user system to a group-based system
-- where multiple users can be part of the same group and see shared data

-- Step 1: Create a groups table
CREATE TABLE IF NOT EXISTS `groups` (
  `id` varchar(36) NOT NULL DEFAULT (uuid()),
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Step 2: Add group_id column to accounts table
ALTER TABLE `accounts` 
ADD COLUMN `group_id` varchar(36) DEFAULT NULL AFTER `email`,
ADD KEY `idx_accounts_group_id` (`group_id`);

-- Step 3: Create a default group for existing users
INSERT INTO `groups` (`id`, `name`, `description`) 
VALUES ('default-group-001', 'Default Group', 'Default group for existing users');

-- Step 4: Assign all existing users to the default group
UPDATE `accounts` 
SET `group_id` = 'default-group-001' 
WHERE `group_id` IS NULL;

-- Step 5: Add group_id column to collection table (this is the main data table)
ALTER TABLE `collection` 
ADD COLUMN `group_id` varchar(36) DEFAULT NULL AFTER `account`,
ADD KEY `idx_collection_group_id` (`group_id`);

-- Step 6: Populate group_id in collection table based on account
UPDATE `collection` c
INNER JOIN `accounts` a ON c.account = a.id
SET c.group_id = a.group_id;

-- Step 7: Add group_id column to expenses table
ALTER TABLE `expenses` 
ADD COLUMN `group_id` varchar(36) DEFAULT NULL AFTER `account`,
ADD KEY `idx_expenses_group_id` (`group_id`);

-- Step 8: Populate group_id in expenses table based on account
UPDATE `expenses` e
INNER JOIN `accounts` a ON e.account = a.id
SET e.group_id = a.group_id;

-- Step 9: Add group_id column to cases table
ALTER TABLE `cases` 
ADD COLUMN `group_id` varchar(36) DEFAULT NULL AFTER `account`,
ADD KEY `idx_cases_group_id` (`group_id`);

-- Step 10: Populate group_id in cases table based on account
UPDATE `cases` c
INNER JOIN `accounts` a ON c.account = a.id
SET c.group_id = a.group_id;

-- Step 11: Add group_id column to categories table (if it exists)
-- First check if categories table has user_id column
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'categories' 
     AND COLUMN_NAME = 'user_id') > 0,
    'ALTER TABLE `categories` ADD COLUMN `group_id` varchar(36) DEFAULT NULL AFTER `user_id`, ADD KEY `idx_categories_group_id` (`group_id`)',
    'SELECT "categories table does not have user_id column" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Step 12: Populate group_id in categories table based on user_id
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'categories' 
     AND COLUMN_NAME = 'user_id') > 0,
    'UPDATE `categories` c INNER JOIN `accounts` a ON c.user_id = a.id SET c.group_id = a.group_id',
    'SELECT "categories table does not have user_id column" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Step 13: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_collection_group_date ON collection(group_id, date);
CREATE INDEX IF NOT EXISTS idx_expenses_group_date ON expenses(group_id, date);
CREATE INDEX IF NOT EXISTS idx_cases_group_name ON cases(group_id, name);

-- Step 14: Add foreign key constraints (optional, for data integrity)
-- Note: These might fail if there are orphaned records, so we'll make them optional
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'accounts' 
     AND COLUMN_NAME = 'group_id') > 0,
    'ALTER TABLE `accounts` ADD CONSTRAINT `fk_accounts_group` FOREIGN KEY (`group_id`) REFERENCES `groups`(`id`) ON DELETE SET NULL',
    'SELECT "accounts group_id column not found" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Step 15: Create a view for easy group management
CREATE OR REPLACE VIEW `group_members` AS
SELECT 
    g.id as group_id,
    g.name as group_name,
    g.description,
    a.id as user_id,
    a.username,
    a.email,
    a.is_admin,
    g.created_at,
    g.updated_at
FROM `groups` g
LEFT JOIN `accounts` a ON g.id = a.group_id
ORDER BY g.name, a.username;

-- Step 16: Create a function to get group statistics
DELIMITER //
CREATE FUNCTION IF NOT EXISTS get_group_stats(group_uuid VARCHAR(36))
RETURNS JSON
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE result JSON;
    
    SELECT JSON_OBJECT(
        'group_id', group_uuid,
        'total_collections', COALESCE(collection_count, 0),
        'total_items', COALESCE(item_count, 0),
        'total_sales', COALESCE(sale_count, 0),
        'total_expenses', COALESCE(expense_count, 0),
        'total_profit', COALESCE(profit_amount, 0)
    ) INTO result
    FROM (
        SELECT 
            (SELECT COUNT(*) FROM collection WHERE group_id = group_uuid) as collection_count,
            (SELECT COUNT(*) FROM items i INNER JOIN collection c ON i.group_id = c.id WHERE c.group_id = group_uuid) as item_count,
            (SELECT COUNT(*) FROM sale s INNER JOIN items i ON s.id = i.id INNER JOIN collection c ON i.group_id = c.id WHERE c.group_id = group_uuid) as sale_count,
            (SELECT COUNT(*) FROM expenses WHERE group_id = group_uuid) as expense_count,
            (SELECT COALESCE(SUM(s.price - s.shipping_fee - COALESCE(s.returned_fee, 0) - c.price), 0) 
             FROM sale s 
             INNER JOIN items i ON s.id = i.id 
             INNER JOIN collection c ON i.group_id = c.id 
             WHERE c.group_id = group_uuid) as profit_amount
    ) stats;
    
    RETURN result;
END //
DELIMITER ;

-- Step 17: Add some sample groups for testing (optional)
INSERT INTO `groups` (`id`, `name`, `description`) VALUES 
('group-family-001', 'Family Group', 'Shared family selling group'),
('group-business-001', 'Business Group', 'Business partnership group'),
('group-friends-001', 'Friends Group', 'Group of friends selling together');

-- Step 18: Create a procedure to move users between groups
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS move_user_to_group(
    IN user_uuid VARCHAR(36),
    IN new_group_uuid VARCHAR(36)
)
BEGIN
    DECLARE old_group_uuid VARCHAR(36);
    
    -- Get current group
    SELECT group_id INTO old_group_uuid FROM accounts WHERE id = user_uuid;
    
    -- Update user's group
    UPDATE accounts SET group_id = new_group_uuid WHERE id = user_uuid;
    
    -- Log the change (you might want to create a log table)
    SELECT CONCAT('User ', user_uuid, ' moved from group ', old_group_uuid, ' to group ', new_group_uuid) as result;
END //
DELIMITER ;

-- Step 19: Create a procedure to create a new group with a user
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS create_group_with_user(
    IN group_name VARCHAR(100),
    IN group_description TEXT,
    IN user_uuid VARCHAR(36)
)
BEGIN
    DECLARE new_group_uuid VARCHAR(36);
    
    -- Create new group
    INSERT INTO `groups` (`name`, `description`) VALUES (group_name, group_description);
    SET new_group_uuid = LAST_INSERT_ID();
    
    -- Move user to new group
    CALL move_user_to_group(user_uuid, new_group_uuid);
    
    SELECT new_group_uuid as group_id;
END //
DELIMITER ;

-- Step 20: Final verification queries
SELECT 'Migration completed successfully!' as status;

-- Show group statistics
SELECT 
    g.name as group_name,
    COUNT(a.id) as member_count,
    COUNT(c.id) as collection_count,
    COUNT(e.id) as expense_count
FROM `groups` g
LEFT JOIN `accounts` a ON g.id = a.group_id
LEFT JOIN `collection` c ON g.id = c.group_id
LEFT JOIN `expenses` e ON g.id = e.group_id
GROUP BY g.id, g.name
ORDER BY g.name;
