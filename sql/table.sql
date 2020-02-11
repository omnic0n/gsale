CREATE TABLE items (
     id MEDIUMINT NOT NULL AUTO_INCREMENT,
     name CHAR(50) NOT NULL,
     sold BOOLEAN NOT NULL DEFAULT 0,
     platform CHAR(120) NOT NULL,
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

CREATE TABLE platform (
     id MEDIUMINT NOT NULL AUTO_INCREMENT,
     name CHAR(50) NOT NULL,
     company CHAR(50) NOT NULL,
     long_name CHAR(50) NOT NULL,
     PRIMARY KEY (id),
     UNIQUE (name)
);

INSERT INTO platform (id, company, name, long_name) values 
('', 'nintendo', 'n64', 'Nintendo 64'), 
('', 'nintendo', 'nes', 'Nintendo NES'), 
('', 'nintendo', 'snes', 'Super Nintendo'), 
('', 'nintendo', 'gamecube', 'Game Cube'), 
('', 'nintendo', 'wii', 'Wii'), 
('', 'nintendo', 'wiiu', 'Wii U'), 
('', 'nintendo', 'switch', 'Switch'),
('', 'nintendo', 'gameboy', 'Gameboy'),
('', 'nintendo', 'gameboycolor', 'Gameboy Color'), 
('', 'nintendo', 'nintendods', 'Nintendo DS'), 
('', 'nintendo', 'nintendo3ds', 'Nintendo 3DS'), 
('', 'sony', 'ps1', 'Playstation 1'),
('', 'sony', 'ps2', 'Playstation 2'),
('', 'sony', 'ps3', 'Playstation 3'), 
('', 'sony', 'ps4', 'Playstation 4'),
('', 'sony', 'psp', 'PSP'),
('', 'sony', 'psvita', 'Playstation Vita'),
('', 'microsoft', 'xbox', 'Xbox'),
('', 'microsoft', 'xbox360', 'Xbox 360'),
('', 'microsoft', 'xboxone', 'Xbox One'),
('', 'sega', 'genesis', 'Sega Genesis'),
('', 'sega', 'mastersystem', 'Sega Master System'),
('', 'sega', 'segacd', 'Sega CD'),
('', 'sega', 'sega32x', 'Sega 32X'),
('', 'sega', 'saturn', 'Sega Saturn'),
('', 'sega', 'dreamcast', 'Sega Dreamcast'),
('', 'sega', 'gamegear', 'Sega Game Gear'),
('', 'other', 'other', 'Other');