-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: localhost    Database: gsale
-- ------------------------------------------------------
-- Server version	8.0.42-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts` (
  `id` varchar(36) NOT NULL DEFAULT (uuid()),
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cases`
--

DROP TABLE IF EXISTS `cases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cases` (
  `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `name` char(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `platform` int DEFAULT NULL,
  `account` varchar(36) DEFAULT NULL,
  KEY `idx_cases_account` (`account`),
  KEY `idx_cases_platform` (`platform`),
  KEY `idx_cases_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` mediumint NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_categories_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collection`
--

DROP TABLE IF EXISTS `collection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collection` (
  `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `date` date NOT NULL,
  `price` decimal(6,2) NOT NULL,
  `name` char(120) NOT NULL,
  `image` char(75) DEFAULT NULL,
  `account` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_collection_account` (`account`),
  KEY `idx_collection_date` (`date`),
  KEY `idx_collection_account_date` (`account`,`date`),
  KEY `idx_collection_date_account` (`date`,`account`),
  KEY `idx_collection_price` (`price`),
  KEY `idx_collection_dayofweek` ((dayofweek(`date`)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `expenses`
--

DROP TABLE IF EXISTS `expenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expenses` (
  `id` varchar(36) NOT NULL DEFAULT (uuid()),
  `date` date NOT NULL,
  `type` int NOT NULL DEFAULT '0',
  `milage` float DEFAULT '0',
  `name` char(50) DEFAULT NULL,
  `price` decimal(6,2) DEFAULT '0.00',
  `image` char(75) DEFAULT NULL,
  `account` varchar(36) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_expenses_account` (`account`),
  KEY `idx_expenses_date` (`date`),
  KEY `idx_expenses_type` (`type`),
  KEY `idx_expenses_account_date` (`account`,`date`),
  KEY `idx_expenses_date_type` (`date`,`type`),
  KEY `idx_expenses_account_type` (`account`,`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `expenses_choices`
--

DROP TABLE IF EXISTS `expenses_choices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expenses_choices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` char(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `sold` tinyint(1) NOT NULL DEFAULT '0',
  `group_id` varchar(36) DEFAULT NULL,
  `category_id` mediumint DEFAULT '0',
  `returned` tinyint(1) unsigned zerofill NOT NULL DEFAULT '0',
  `storage` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'None',
  `list_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_items_group_id` (`group_id`),
  KEY `idx_items_sold` (`sold`),
  KEY `idx_items_category_id` (`category_id`),
  KEY `idx_items_storage` (`storage`),
  KEY `idx_items_list_date` (`list_date`),
  KEY `idx_items_group_sold` (`group_id`,`sold`),
  KEY `idx_items_sale_collection` (`id`,`group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `platform`
--

DROP TABLE IF EXISTS `platform`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `platform` (
  `id` int DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  KEY `idx_platform_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sale`
--

DROP TABLE IF EXISTS `sale`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sale` (
  `date` date NOT NULL,
  `price` decimal(6,2) NOT NULL,
  `shipping_fee` decimal(5,2) DEFAULT '0.00',
  `id` varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  KEY `idx_sale_id` (`id`),
  KEY `idx_sale_date` (`date`),
  KEY `idx_sale_price` (`price`),
  KEY `idx_sale_date_account` (`date`,`id`),
  KEY `idx_sale_price_shipping` (`price`,`shipping_fee`),
  KEY `idx_sale_items_collection` (`id`,`date`),
  KEY `idx_sale_dayofweek` ((dayofweek(`date`)))
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `years`
--

DROP TABLE IF EXISTS `years`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `years` (
  `year` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-29 23:41:20


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
