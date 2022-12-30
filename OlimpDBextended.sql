-- MySQL dump 10.13  Distrib 8.0.18, for macos10.14 (x86_64)
--
-- Host: localhost    Database: olimp
-- ------------------------------------------------------
-- Server version	8.0.18

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
-- Table structure for table `Dismissal_info`
--

DROP TABLE IF EXISTS `Dismissal_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Dismissal_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reason_id` int(11) NOT NULL,
  `short_reason` varchar(100) NOT NULL,
  `full_reason` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reason_id` (`reason_id`),
  UNIQUE KEY `short_reason` (`short_reason`),
  UNIQUE KEY `full_reason` (`full_reason`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Dismissal_info`
--

LOCK TABLES `Dismissal_info` WRITE;
/*!40000 ALTER TABLE `Dismissal_info` DISABLE KEYS */;
INSERT INTO `Dismissal_info` VALUES (1,3,'пт. 3 ст.77 ТК РФ','Расторжение трудового договора по инициативе работника'),(2,2,'пт.10 ст.77 ТК РФ','Обстоятельства, не зависящие от воли сторон'),(3,5,'пт. 5 ст.81 ТК РФ','Неоднократное неисполнение работником трудовых обязанностей'),(4,6,'пт. 6а ст.81 ТК РФ','Однократное грубое нарушение работником трудовых обязанностей: прогул');
/*!40000 ALTER TABLE `Dismissal_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Document`
--

DROP TABLE IF EXISTS `Document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Document` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `doc_id` int(11) NOT NULL,
  `doc_name` varchar(100) NOT NULL,
  `time` float NOT NULL,
  `number` int(11) NOT NULL,
  `period` float NOT NULL,
  `function_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `doc_id` (`doc_id`),
  UNIQUE KEY `doc_name` (`doc_name`),
  KEY `function_id` (`function_id`),
  CONSTRAINT `document_ibfk_1` FOREIGN KEY (`function_id`) REFERENCES `func` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Document`
--

LOCK TABLES `Document` WRITE;
/*!40000 ALTER TABLE `Document` DISABLE KEYS */;
INSERT INTO `Document` VALUES (7,632,'График разработки ППР',8.5,3,1,6),(8,624,'ППР',70,3,1,6),(9,635,'ПОС',80,3,1,6),(10,610,'Технологические карты',75,1,0.2,6);
/*!40000 ALTER TABLE `Document` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `exist_spec`
--

DROP TABLE IF EXISTS `exist_spec`;
/*!50001 DROP VIEW IF EXISTS `exist_spec`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `exist_spec` AS SELECT 
 1 AS `struct_subdivision`,
 1 AS `function_name`,
 1 AS `number_of_exist_spec`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `Func`
--

DROP TABLE IF EXISTS `Func`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Func` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `function_id` int(11) NOT NULL,
  `function_name` varchar(100) NOT NULL,
  `struct_subdivision` varchar(100) NOT NULL,
  `salary` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `function_id` (`function_id`,`function_name`),
  UNIQUE KEY `function_name` (`function_name`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Func`
--

LOCK TABLES `Func` WRITE;
/*!40000 ALTER TABLE `Func` DISABLE KEYS */;
INSERT INTO `Func` VALUES (6,21229,'Главный технолог','Отдел главного технолога',50000),(21,13383,'Заместитель директора','Администрация',45000),(22,13900,'Главный бухгалтер','Бухгалтерия',32000),(23,11518,'Бухгалтер','Бухгалтерия',45000),(24,13597,'Начальний отдела кадров','Отдел кадров',25000),(25,12454,'Ведущий бухгалтер','Бухгалтерия',45000),(26,13481,'Менеджер отдела закупок','Отдел закупок',35000),(27,13825,'Начальник отдела закупок','Отдел закупок',25000),(28,14956,'Специалист по кадрам','Отдел кадров',35000),(29,11993,'Главный инженер','Администрация',45000),(30,15429,'Офис-менеджер','Администрация',25000),(31,15005,'Инженер по охране труда','Отдел кадров',32000),(32,13803,'Начальник склада','Склад',45000),(33,13385,'Кладовщик','Склад',35000),(34,13901,'Инспектор','Администрация',45000),(38,22222,'Разнорабочий','Склад',32000);
/*!40000 ALTER TABLE `Func` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `missing_unit_info`
--

DROP TABLE IF EXISTS `missing_unit_info`;
/*!50001 DROP VIEW IF EXISTS `missing_unit_info`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `missing_unit_info` AS SELECT 
 1 AS `struct_subdivision`,
 1 AS `function_name`,
 1 AS `number_of_spec`,
 1 AS `number_of_exist_spec`,
 1 AS `deviation`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `Order_of_dismissal`
--

DROP TABLE IF EXISTS `Order_of_dismissal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Order_of_dismissal` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `order_date` date NOT NULL,
  `true_reason` varchar(200) DEFAULT NULL,
  `spec_id` int(11) NOT NULL,
  `reas_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`),
  KEY `spec_id` (`spec_id`),
  KEY `reas_id` (`reas_id`),
  CONSTRAINT `order_of_dismissal_ibfk_1` FOREIGN KEY (`spec_id`) REFERENCES `specialist` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `order_of_dismissal_ibfk_2` FOREIGN KEY (`reas_id`) REFERENCES `dismissal_info` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Order_of_dismissal`
--

LOCK TABLES `Order_of_dismissal` WRITE;
/*!40000 ALTER TABLE `Order_of_dismissal` DISABLE KEYS */;
INSERT INTO `Order_of_dismissal` VALUES (29,715,'2020-03-25','Неудобное местоположение',2,3),(30,720,'2021-04-08',NULL,3,4),(31,717,'2022-04-16','Недовольство начальником',4,1),(32,723,'2021-02-25','Маленькая зарплата',5,1),(33,724,'2022-05-27',NULL,6,3),(34,725,'2020-06-16','Недовольство начальником',7,1),(35,721,'2021-06-30',NULL,8,4),(36,718,'2020-07-21','Маленькая зарплата',9,1),(37,716,'2022-07-28',NULL,10,2),(38,719,'2021-08-23',NULL,11,2),(39,722,'2022-08-25','Маленькая зарплата',12,1),(40,728,'2020-08-30',NULL,13,3),(41,726,'2022-09-17',NULL,14,3),(42,727,'2015-09-20','Недовольство начальником',15,1);
/*!40000 ALTER TABLE `Order_of_dismissal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Specialist`
--

DROP TABLE IF EXISTS `Specialist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Specialist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `spec_id` int(11) NOT NULL,
  `spec_name` varchar(200) NOT NULL,
  `birthday` date NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `function_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `spec_id` (`spec_id`),
  KEY `function_id` (`function_id`),
  CONSTRAINT `specialist_ibfk_1` FOREIGN KEY (`function_id`) REFERENCES `func` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Specialist`
--

LOCK TABLES `Specialist` WRITE;
/*!40000 ALTER TABLE `Specialist` DISABLE KEYS */;
INSERT INTO `Specialist` VALUES (1,237,'Елисеев Станислав Юлианович','1986-05-27','2002-02-01',NULL,6),(2,173,'Русаков В.В.','1988-02-15','2007-04-29','2020-03-25',21),(3,212,'Савельев О.О.','1992-04-01','2003-05-08','2021-04-08',22),(4,236,'Самсонов Д.Е.','1985-03-18','2008-12-20','2022-04-16',23),(5,216,'Сидоров К.К.','1982-10-24','2009-02-01','2021-02-25',24),(6,243,'Снитко А.П','1977-11-13','2015-10-20','2022-05-27',25),(7,241,'Тимофеев А.П.','1988-08-11','2016-12-14','2020-06-16',26),(8,217,'Титов Р.К.','1990-12-01','2020-08-06','2021-06-30',27),(9,203,'Третьяков В.Д.','1985-02-16','2014-03-14','2020-07-21',28),(10,227,'Третьяков М.В.','1986-04-17','2014-08-25','2022-07-28',29),(11,239,'Трофимов Л.Е.','1982-12-25','2009-01-08','2021-08-23',30),(12,221,'Уланов Г.Г.','1986-10-04','2010-08-13','2022-08-25',31),(13,225,'Ульянов П.В.','1986-05-11','2018-04-21','2020-08-30',32),(14,201,'Федосеев П.Р.','1979-12-25','2013-03-03','2022-09-17',33),(15,200,'Фролов А.Д.','1988-02-15','2007-04-29','2015-09-20',34);
/*!40000 ALTER TABLE `Specialist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `stuff_list`
--

DROP TABLE IF EXISTS `stuff_list`;
/*!50001 DROP VIEW IF EXISTS `stuff_list`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `stuff_list` AS SELECT 
 1 AS `struct_subdivision`,
 1 AS `function_name`,
 1 AS `number_of_spec`,
 1 AS `salary`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `Work_time_info`
--

DROP TABLE IF EXISTS `Work_time_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Work_time_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `current_year` int(11) NOT NULL,
  `hour_year` int(11) NOT NULL,
  `hour_day` int(11) NOT NULL DEFAULT '8',
  `day_year` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `current_year` (`current_year`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Work_time_info`
--

LOCK TABLES `Work_time_info` WRITE;
/*!40000 ALTER TABLE `Work_time_info` DISABLE KEYS */;
INSERT INTO `Work_time_info` VALUES (1,2023,1976,8,247);
/*!40000 ALTER TABLE `Work_time_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `exist_spec`
--

/*!50001 DROP VIEW IF EXISTS `exist_spec`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `exist_spec` AS select `f`.`struct_subdivision` AS `struct_subdivision`,`f`.`function_name` AS `function_name`,count(`sp`.`id`) AS `number_of_exist_spec` from (`func` `f` join `specialist` `sp` on((`f`.`id` = `sp`.`function_id`))) where (`sp`.`end_date` is null) group by `f`.`function_name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `missing_unit_info`
--

/*!50001 DROP VIEW IF EXISTS `missing_unit_info`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `missing_unit_info` AS select `sl`.`struct_subdivision` AS `struct_subdivision`,`sl`.`function_name` AS `function_name`,`sl`.`number_of_spec` AS `number_of_spec`,`es`.`number_of_exist_spec` AS `number_of_exist_spec`,(`sl`.`number_of_spec` - `es`.`number_of_exist_spec`) AS `deviation` from (`stuff_list` `sl` join `exist_spec` `es` on((`sl`.`function_name` = `es`.`function_name`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `stuff_list`
--

/*!50001 DROP VIEW IF EXISTS `stuff_list`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `stuff_list` AS select `f`.`struct_subdivision` AS `struct_subdivision`,`f`.`function_name` AS `function_name`,floor(ceiling((sum(((`d`.`number` * `d`.`period`) * `d`.`time`)) / `wti`.`hour_year`))) AS `number_of_spec`,`f`.`salary` AS `salary` from ((`func` `f` join `document` `d` on((`f`.`id` = `d`.`function_id`))) join `work_time_info` `wti` on((`wti`.`current_year` = '2023'))) group by `f`.`function_name` order by `f`.`function_name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-12-30 18:42:15
