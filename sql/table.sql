CREATE TABLE items (
     id MEDIUMINT NOT NULL AUTO_INCREMENT,
     group_id MEDIUMINT,
     name CHAR(50) NOT NULL,
     sold BOOLEAN NOT NULL DEFAULT 0,
     description CHAR(120) NOT NULL,
     PRIMARY KEY (id)
);

CREATE TABLE purchase (
     id MEDIUMINT NOT NULL,
     location MEDIUMINT NOT NULL,
     date DATE NOT NULL,
     price  DECIMAL(6,2) NOT NULL
);

CREATE TABLE sale (
     id MEDIUMINT NOT NULL,
     location MEDIUMINT NOT NULL,
     date DATE NOT NULL,
     price  DECIMAL(6,2) NOT NULL,
     price_tax DECIMAL(6,2),
     ebay_fee DECIMAL(6,2),
     paypal_fee DECIMAL(6,2),
     shipping_fee DECIMAL(5,2)
);

CREATE TABLE groups (
     id MEDIUMINT NOT NULL AUTO_INCREMENT,
     name CHAR(50) NOT NULL,
     PRIMARY KEY (id),
     UNIQUE (name)
);

CREATE TABLE location (
     id MEDIUMINT NOT NULL AUTO_INCREMENT,
     name CHAR(50) NOT NULL,
     long_name CHAR(50) NOT NULL,
     PRIMARY KEY (id),
     UNIQUE (name)
);

INSERT INTO location (id, name, long_name) values 
('', 'garagesale', 'Garage Sale'), 
('', 'thrift', 'Thrift Store'), 
('', 'pawn', 'Pawn Shop'), 
('', 'ebay', 'Ebay'), 
('', 'facebook', 'Facebook Marketplace'), 
('', 'hibid', 'Hibid'), 
('', 'brockbuysgames', 'BrockBuysGames'), 
('', 'halfpricebooks', 'Half Price Books');