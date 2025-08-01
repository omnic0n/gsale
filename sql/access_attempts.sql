-- Create table to track access attempts from unauthorized users
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
CREATE INDEX idx_access_attempts_email ON access_attempts(email);
CREATE INDEX idx_access_attempts_status ON access_attempts(status);
CREATE INDEX idx_access_attempts_attempted_at ON access_attempts(attempted_at); 