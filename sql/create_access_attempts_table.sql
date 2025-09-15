-- Create access_attempts table if it doesn't exist
-- This is needed for the admin panel to work properly

CREATE TABLE IF NOT EXISTS access_attempts (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    google_id VARCHAR(100),
    name VARCHAR(255),
    picture VARCHAR(500),
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    status ENUM('pending', 'approved', 'denied') DEFAULT 'pending'
);

-- Add indexes for better performance
-- Check if indexes exist before creating them
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'access_attempts' 
     AND INDEX_NAME = 'idx_access_attempts_email') = 0,
    'CREATE INDEX idx_access_attempts_email ON access_attempts(email)',
    'SELECT "idx_access_attempts_email index already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'access_attempts' 
     AND INDEX_NAME = 'idx_access_attempts_status') = 0,
    'CREATE INDEX idx_access_attempts_status ON access_attempts(status)',
    'SELECT "idx_access_attempts_status index already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'access_attempts' 
     AND INDEX_NAME = 'idx_access_attempts_attempted_at') = 0,
    'CREATE INDEX idx_access_attempts_attempted_at ON access_attempts(attempted_at)',
    'SELECT "idx_access_attempts_attempted_at index already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
