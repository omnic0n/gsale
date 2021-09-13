CREATE TABLE items (
     id MEDIUMINT NOT NULL AUTO_INCREMENT,
     name CHAR(50) NOT NULL,
     sold BOOLEAN NOT NULL DEFAULT 0,
     platform CHAR(120) NOT NULL,
     group_id MEDIUMINT DEFAULT NULL,
     PRIMARY KEY (id)
);

CREATE TABLE groups (
     id MEDIUMINT NOT NULL AUTO_INCREMENT,
     date DATE NOT NULL,
     price  DECIMAL(6,2) NOT NULL,
     name CHAR(120) NOT NULL,
     PRIMARY KEY (id),
     UNIQUE (name)
);

CREATE TABLE purchase (
     id MEDIUMINT NOT NULL,
     date DATE,
     price  DECIMAL(6,2),
);

CREATE TABLE sale (
     id MEDIUMINT NOT NULL,
     date DATE NOT NULL,
     price  DECIMAL(6,2) NOT NULL,
     shipping_fee DECIMAL(5,2) DEFAULT 0.00
);