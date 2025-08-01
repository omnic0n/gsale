-- Add location columns to collection table
ALTER TABLE collection 
ADD COLUMN latitude DECIMAL(10, 8) NULL,
ADD COLUMN longitude DECIMAL(11, 8) NULL,
ADD COLUMN location_name VARCHAR(255) NULL,
ADD COLUMN location_address TEXT NULL;

-- Add indexes for location queries
CREATE INDEX idx_collection_location ON collection(latitude, longitude);
CREATE INDEX idx_collection_location_name ON collection(location_name); 