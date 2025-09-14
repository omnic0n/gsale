-- Check the current structure of the categories table
-- Run this first to see what columns and constraints exist

SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    EXTRA,
    COLUMN_KEY
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
AND TABLE_NAME = 'categories'
ORDER BY ORDINAL_POSITION;

-- Check for auto-increment columns
SELECT 
    COLUMN_NAME,
    EXTRA
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
AND TABLE_NAME = 'categories' 
AND EXTRA LIKE '%auto_increment%';

-- Check primary key
SELECT 
    COLUMN_NAME,
    CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = DATABASE() 
AND TABLE_NAME = 'categories' 
AND CONSTRAINT_NAME = 'PRIMARY';
