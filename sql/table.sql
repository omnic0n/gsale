CREATE TABLE items (
     id MEDIUMINT NOT NULL AUTO_INCREMENT,
     group_id MEDIUMINT,
     name CHAR(50) NOT NULL,
     description CHAR(120) NOT NULL,
     PRIMARY KEY (id),
);

CREATE TABLE purchase (
     id MEDIUMINT NOT NULL,
     location CHAR(50) NOT NULL,
     date DATE NOT NULL,
     price  DECIMAL(6,2) NOT NULL
);

CREATE TABLE sale (
     id MEDIUMINT NOT NULL,
     location CHAR(50) NOT NULL,
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
