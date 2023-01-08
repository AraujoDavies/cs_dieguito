CREATE DATABASE  IF NOT EXISTS `entradas_test` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `entradas_test`;
-- MySQL dump 10.13  Distrib 8.0.30, for Win64 (x86_64)
--
-- Host: localhost    Database: entradas_test
-- ------------------------------------------------------
-- Server version	8.0.30

--
-- Table structure for table `cs_entradas_concluidas`
--

DROP TABLE IF EXISTS `cs_entradas_concluidas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cs_entradas_concluidas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `jogo` varchar(250) NOT NULL,
  `profit_loss` varchar(45) NOT NULL,
  `favorito` varchar(45) NOT NULL,
  `odd_entrada` float NOT NULL,
  `odd_saida` float NOT NULL,
  `competicao` varchar(45) NOT NULL,
  `profit_loss_ht` varchar(45) DEFAULT 'NA',
  `placar_ht` varchar(45) DEFAULT 'Indefinido',
  PRIMARY KEY (`id`)
);

--
-- Table structure for table `cs_entradas_em_andamento`
--

DROP TABLE IF EXISTS `cs_entradas_em_andamento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cs_entradas_em_andamento` (
  `id` int NOT NULL AUTO_INCREMENT,
  `jogo` varchar(250) NOT NULL,
  `placar` varchar(45) NOT NULL,
  `odd_entrada` float NOT NULL,
  `favorito` tinyint NOT NULL,
  `id_msg_telegram` int NOT NULL,
  `url` varchar(500) NOT NULL,
  `competicao` varchar(45) NOT NULL,
  `profit_loss_ht` varchar(45) DEFAULT 'NA',
  `placar_ht` varchar(45) DEFAULT 'Indefinido',
  PRIMARY KEY (`id`)
);

--
-- Table structure for table `cs_jogos_do_dia`
--

DROP TABLE IF EXISTS `cs_jogos_do_dia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cs_jogos_do_dia` (
  `id` int NOT NULL AUTO_INCREMENT,
  `jogo` varchar(250) NOT NULL,
  `favorito` tinyint NOT NULL COMMENT '0 = mandante\n1 = visitante',
  `odd_mandante` float NOT NULL,
  `odd_visitante` float NOT NULL,
  `data_inicio` datetime DEFAULT NULL,
  `competicao` varchar(45) NOT NULL,
  `url` varchar(500) NOT NULL,
  PRIMARY KEY (`id`)
);