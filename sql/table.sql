-- MySQL dump 10.13  Distrib 5.7.36, for Linux (x86_64)
--
-- Host: localhost    Database: gsale
-- ------------------------------------------------------
-- Server version	5.7.36-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categories` (
  `id` mediumint(9) NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `expenses`
--

DROP TABLE IF EXISTS `expenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `expenses` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `type` int(11) NOT NULL DEFAULT '0',
  `milage` float DEFAULT NULL,
  `name` char(50) DEFAULT NULL,
  `price` float DEFAULT NULL,
  `image` char(75) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `price` decimal(6,2) NOT NULL,
  `name` char(120) NOT NULL,
  `image` char(75) DEFAULT NULL
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `items` (
  `id` mediumint(9) NOT NULL AUTO_INCREMENT,
  `name` char(50) NOT NULL,
  `sold` tinyint(1) NOT NULL DEFAULT '0',
  `group_id` mediumint(9) DEFAULT NULL,
  `category_id` mediumint(9) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=357 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sale`
--

DROP TABLE IF EXISTS `sale`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sale` (
  `id` mediumint(9) NOT NULL,
  `date` date NOT NULL,
  `price` decimal(6,2) NOT NULL,
  `shipping_fee` decimal(5,2) DEFAULT '0.00'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-03-22  0:05:27

-- Add performance indexes for better query performance
-- These indexes will significantly improve the speed of your most common queries

-- Collection table indexes
CREATE INDEX idx_collection_account ON collection(account);
CREATE INDEX idx_collection_date ON collection(date);
CREATE INDEX idx_collection_account_date ON collection(account, date);

-- Items table indexes  
CREATE INDEX idx_items_group_id ON items(group_id);
CREATE INDEX idx_items_sold ON items(sold);
CREATE INDEX idx_items_category_id ON items(category_id);
CREATE INDEX idx_items_storage ON items(storage);
CREATE INDEX idx_items_list_date ON items(list_date);
CREATE INDEX idx_items_group_sold ON items(group_id, sold);

-- Sale table indexes
CREATE INDEX idx_sale_id ON sale(id);
CREATE INDEX idx_sale_date ON sale(date);
CREATE INDEX idx_sale_price ON sale(price);

-- Expenses table indexes
CREATE INDEX idx_expenses_account ON expenses(account);
CREATE INDEX idx_expenses_date ON expenses(date);
CREATE INDEX idx_expenses_type ON expenses(type);
CREATE INDEX idx_expenses_account_date ON expenses(account, date);

-- Categories table index
CREATE INDEX idx_categories_type ON categories(type);

-- Cases table indexes
CREATE INDEX idx_cases_account ON cases(account);
CREATE INDEX idx_cases_platform ON cases(platform);
CREATE INDEX idx_cases_name ON cases(name);

-- Location table index
CREATE INDEX idx_location_group_id ON location(group_id);

-- Platform table index
CREATE INDEX idx_platform_name ON platform(name);

-- Report-specific indexes for better performance
-- Sales report indexes
CREATE INDEX idx_sale_date_account ON sale(date, id);
CREATE INDEX idx_sale_price_shipping ON sale(price, shipping_fee);

-- Purchase report indexes  
CREATE INDEX idx_collection_date_account ON collection(date, account);
CREATE INDEX idx_collection_price ON collection(price);

-- Expenses report indexes
CREATE INDEX idx_expenses_date_type ON expenses(date, type);
CREATE INDEX idx_expenses_account_type ON expenses(account, type);

-- Day of week function indexes for faster filtering
CREATE INDEX idx_sale_dayofweek ON sale((DAYOFWEEK(date)));
CREATE INDEX idx_collection_dayofweek ON collection((DAYOFWEEK(date)));

-- Composite indexes for common report queries
CREATE INDEX idx_items_sale_collection ON items(id, group_id);
CREATE INDEX idx_sale_items_collection ON sale(id, date);
