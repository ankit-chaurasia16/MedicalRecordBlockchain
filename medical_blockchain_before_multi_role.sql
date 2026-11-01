-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: medical_blockchain
-- ------------------------------------------------------
-- Server version	8.0.46

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
-- Table structure for table `doctor_patient`
--

DROP TABLE IF EXISTS `doctor_patient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `doctor_patient` (
  `assignment_id` int NOT NULL AUTO_INCREMENT,
  `doctor_id` int NOT NULL,
  `patient_id` int NOT NULL,
  `assigned_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('pending','in_progress','completed') NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`assignment_id`),
  UNIQUE KEY `unique_assignment` (`doctor_id`,`patient_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `doctor_patient_ibfk_1` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`),
  CONSTRAINT `doctor_patient_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `doctor_patient`
--

LOCK TABLES `doctor_patient` WRITE;
/*!40000 ALTER TABLE `doctor_patient` DISABLE KEYS */;
INSERT INTO `doctor_patient` VALUES (1,1,1,'2026-11-01 19:23:27','pending');
/*!40000 ALTER TABLE `doctor_patient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `doctors`
--

DROP TABLE IF EXISTS `doctors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `doctors` (
  `doctor_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `specialization` varchar(100) DEFAULT NULL,
  `license_number` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `department` varchar(100) NOT NULL DEFAULT 'General Medicine',
  `qualification` varchar(150) DEFAULT NULL,
  `years_experience` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`doctor_id`),
  UNIQUE KEY `license_number` (`license_number`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `doctors`
--

LOCK TABLES `doctors` WRITE;
/*!40000 ALTER TABLE `doctors` DISABLE KEYS */;
INSERT INTO `doctors` VALUES (1,'Dr. Amit Kumar','General Medicine','DEMO-MC-001','2026-11-01 19:23:27','General Medicine',NULL,0),(2,'Ankit Chaurasia','Interventional Cardiology','12345678','2026-11-01 20:40:02','Cardiology','MBBS',0);
/*!40000 ALTER TABLE `doctors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medical_records`
--

DROP TABLE IF EXISTS `medical_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medical_records` (
  `record_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `doctor_id` int DEFAULT NULL,
  `diagnosis` varchar(255) NOT NULL,
  `prescription` text,
  `doctor_name` varchar(100) DEFAULT NULL,
  `record_hash` varchar(64) DEFAULT NULL,
  `transaction_hash` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`record_id`),
  KEY `patient_id` (`patient_id`),
  KEY `idx_medical_records_doctor` (`doctor_id`),
  CONSTRAINT `fk_medical_records_doctor` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`),
  CONSTRAINT `medical_records_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medical_records`
--

LOCK TABLES `medical_records` WRITE;
/*!40000 ALTER TABLE `medical_records` DISABLE KEYS */;
INSERT INTO `medical_records` VALUES (1,1,1,'Seasonal Fever','Paracetamol 500 mg, rest and fluids','Dr. Amit Kumar','8f095be865d73dad4d8cca5c8e01e56e6c0d0635a8b431ec3736ecb3bf7a249f','9de8c7481b9c6bedcd910405862d309235f20d5affd791933429d74d18a25a56','2026-11-01 19:00:17'),(2,2,NULL,'Vitamin D Deficiency','Vitamin D supplementation as prescribed','Dr. Neha Gupta','8c8e86f54b55868d6a5c226468124d1da4ba50c92e433c49f7513d8273a58f97','195d168ca9583bc90e745020936e6bde4860d7f09ed3eb463d6087430b310ce1','2026-11-01 19:01:45'),(3,3,NULL,'Seasonal Allergy','Antihistamine as prescribed, avoid allergens','Dr. Raj Malhotra','0d839ce60be3f32470879658882ade48dc6c16a3c4b2dc250d09fab852e1d6a5','f746a7b2ac003fc46351e3d8b83bee0135eda0c0dec9c522e6a74360eb220854','2026-11-01 19:02:57');
/*!40000 ALTER TABLE `medical_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patients`
--

DROP TABLE IF EXISTS `patients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patients` (
  `patient_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `age` int DEFAULT NULL,
  `gender` varchar(20) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `disease_category` varchar(100) NOT NULL DEFAULT 'General Medicine',
  PRIMARY KEY (`patient_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patients`
--

LOCK TABLES `patients` WRITE;
/*!40000 ALTER TABLE `patients` DISABLE KEYS */;
INSERT INTO `patients` VALUES (1,'Rahul Sharma',25,'Male','9000000001','2026-11-01 18:57:31','General Medicine'),(2,'Priya Verma',22,'Female','9000000002','2026-11-01 18:58:20','General Medicine'),(3,'Arjun Singh',30,'Male','9000000003','2026-11-01 18:59:05','General Medicine');
/*!40000 ALTER TABLE `patients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('doctor','patient') NOT NULL,
  `patient_id` int DEFAULT NULL,
  `doctor_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `patient_id` (`patient_id`),
  UNIQUE KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`),
  CONSTRAINT `users_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'doctor@medicalchain.demo','scrypt:32768:8:1$gSTDLBiDXnz2vHc7$750284dd636a4cd59cf489112410318d281ed95276b82a4d5152fd85f564099163677ac87f230c4d1355a6b3773f961cf4bb7a46b7b9255e06df8258d749fc61','doctor',NULL,1,'2026-11-01 19:23:27'),(2,'patient1@medicalchain.demo','scrypt:32768:8:1$8EOaPNXzRDWAVBNa$306a32b5fe6da7b4aef7ab0ca6a8eade4aabb4f0b516d268359b940d82d538a61037c0396dd70332edc5b5497bbc45bcc44704857af26150fc09c2a611127a40','patient',1,NULL,'2026-11-01 19:23:27'),(3,'patient2@medicalchain.demo','scrypt:32768:8:1$N6uF1PmSJFUyWvgX$7ea32cc601a77ad771e875d13fd03d9382c30a73683817234d25aeba35df92546457f4ffcca12ac57266b850fe4afdb4854e84547d56846ea94126cee1022936','patient',2,NULL,'2026-11-01 19:23:27'),(4,'patient3@medicalchain.demo','scrypt:32768:8:1$taV0DvVU3LlsFPcq$9ba69ef6c304a106f55d2385dabdf9f7f42c9300b187b1885449a04a8f02e4bee04ee1426cbcc9a2b4df2e93bd6b4012891ff93765a2b004233d509b40c521ba','patient',3,NULL,'2026-11-01 19:23:27'),(5,'ankit@000.com','scrypt:32768:8:1$G1YK1G4Su0lLc4U1$3cfc346404a5e1492dca0ceeda646c9d633d0926e0b0e7f2ddd3a0a5f36533efbab1b3cf22558d798bb44548995111e4b8dc44aa2af37e3e5f798b60ac1f33f5','doctor',NULL,2,'2026-11-01 20:40:02');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-02  2:42:32
