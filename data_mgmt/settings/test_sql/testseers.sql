-- MySQL dump 10.13  Distrib 5.1.67, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: testseers
-- ------------------------------------------------------
-- Server version	5.1.67

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
-- Table structure for table `authors`
--

DROP TABLE IF EXISTS `authors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `authors` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `cluster` bigint(20) unsigned DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `affil` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `paper_cluster` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `cluster` (`cluster`),
  KEY `name` (`name`),
  KEY `paperid` (`paper_cluster`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authors`
--

LOCK TABLES `authors` WRITE;
/*!40000 ALTER TABLE `authors` DISABLE KEYS */;
INSERT INTO `authors` VALUES (1,1,'Helen Smith','Foo',NULL,'hsmith@foo.com','1'),(2,1,'Helen Smith','Foo',NULL,'hsmith@foo.com','2'),(3,2,'David Johnson','Foo',NULL,'djo@foo.com','2'),(4,2,'David Johnson','Foo',NULL,'djo@foo.com','3'),(5,2,'David Johnson','Foo',NULL,'djo@foo.com','4'),(6,2,'David Johnson','Foo',NULL,'djo@foo.com','5'),(7,3,'Peter Williams','bar',NULL,'pw@bar.edu','3'),(8,4,'Sean Jones','Foo',NULL,'sjo@foo.com','3'),(9,4,'Sean Jones','Foo',NULL,'sjo@foo.com','4'),(10,4,'Sean Jones','Foo',NULL,'sjo@foo.com','6'),(11,4,'Sean Jones','Foo',NULL,'sjo@foo.com','7'),(12,4,'Sean Jones','Foo',NULL,'sjo@foo.com','8'),(13,5,'Jenny Brown','bar',NULL,'jb@bar.edu','9'),(14,5,'Jenny Brown','bar',NULL,'jb@bar.edu','10');
/*!40000 ALTER TABLE `authors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `papers`
--

DROP TABLE IF EXISTS `papers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `papers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cluster` int(11) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `abstract` text,
  `year` int(11) DEFAULT NULL,
  `venue` varchar(255) DEFAULT NULL,
  `ncites` int(10) unsigned NOT NULL DEFAULT '0',
  `pdf_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cluster` (`cluster`),
  KEY `title` (`title`),
  KEY `year` (`year`),
  KEY `ncites` (`ncites`),
  FULLTEXT KEY `title_2` (`title`)
) ENGINE=MyISAM AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `papers`
--

LOCK TABLES `papers` WRITE;
/*!40000 ALTER TABLE `papers` DISABLE KEYS */;
INSERT INTO `papers` VALUES (1,1,'Trans fat','Trans fat is the common name for unsaturated fat with trans-isomer (E-isomer) fatty acid(s). Because the term refers to the configuration of a double carbon-carbon bond, trans fats are sometimes monounsaturated or polyunsaturated, but never saturated. Trans fats do exist in nature but also occur during the processing of polyunsaturated fatty acids in food production.',2001,'Chem. Soc. Rev.',3,NULL),(2,2,'nuclear physics','Nuclear physics is the field of physics that studies the constituents and interactions of atomic nuclei. The most commonly known applications of nuclear physics are nuclear power generation and nuclear weapons technology, but the research has provided application in many fields, including those in nuclear medicine and magnetic resonance imaging, ion implantation in materials engineering, and radiocarbon dating in geology and archaeology.\nThe field of particle physics evolved out of nuclear physics and is typically taught in close association with nuclear physics.',2002,'Chem. Soc. Rev.',20,NULL),(3,3,'Nuclear fusion','In nuclear physics, nuclear fusion is a nuclear reaction in which two or more atomic nuclei join together, or \"fuse\", to form a single heavier nucleus. During this process, matter is not conserved because some of the mass of the fusing nuclei is converted to energy which is released. Fusion is the process that powers active stars.',2004,'Chem. Commun.',10,NULL),(4,4,'Nuclear magnetic resonance','Nuclear magnetic resonance (NMR) is a physical phenomenon quux corge in which magnetic nuclei in a magnetic field absorb and re-emit electromagnetic radiation. This energy is at a specific resonance frequency which depends on the strength of the magnetic field and the magnetic properties of the isotope of the atoms; in practical applications, the frequency is similar to VHF and UHF television broadcasts (60–1000 MHz). NMR allows the observation of specific quantum mechanical magnetic properties of the atomic nucleus. Many scientific techniques exploit NMR phenomena to study molecular physics, crystals, and non-crystalline materials through NMR spectroscopy. NMR is also routinely used in advanced medical imaging techniques, such as in magnetic resonance imaging (MRI).',2006,'Chem. Commun.',5,NULL),(5,5,'Zeeman effect quux corge','The Zeeman effect ( /ˈzeɪmən/; IPA: [ˈzeːmɑn]), named after the Dutch physicist Pieter Zeeman, is the effect of splitting a spectral line into several components in the presence of a static magnetic field. It is analogous to the Stark effect, the splitting of a spectral line into several components in the presence of an electric field. Also similarly to the Stark effect, transitions between different components have, in general, different intensities, with some being entirely forbidden (in the dipole approximation), as governed by the selection rules.',2003,'Chem. Soc. Rev.',9,NULL),(6,6,'Enzyme','Enzymes ( /ˈɛnzaɪmz/) are large biological molecules responsible for the thousands of chemical interconversions that sustain life.[1][2] They are highly selective catalysts, greatly accelerating both the rate and specificity of metabolic reactions, from the digestion of food to the synthesis of DNA. Most enzymes are proteins, although some catalytic RNA molecules have been identified. Enzymes adopt a specific three-dimensional structure, and may employ organic (e.g. biotin) and inorganic (e.g. magnesium ion) cofactors to assist in catalysis.',2003,'Chem. Soc. Rev.',18,NULL),(7,7,'Protein','Proteins ( /ˈproʊˌtiːnz/ or /ˈproʊti.ɨnz/) are large biological molecules consisting of one or more chains of amino acids. Proteins perform a vast array of functions within living organisms, including catalyzing metabolic reactions, replicating DNA, responding to stimuli, and transporting molecules from one location to another. Proteins differ from one another primarily in their sequence of amino acids, which is dictated by the nucleotide sequence of their genes, and which usually results in folding of the protein into a specific three-dimensional structure that determines its activity.',2004,'Chem. Soc. Rev.',14,NULL),(8,8,'Hydrogen peroxide','Hydrogen peroxide (H2O2) is the simplest peroxide (a compound with an oxygen-oxygen single bond). It is also a strong oxidizer. Hydrogen peroxide is a clear liquid, slightly more viscous than water. In dilute solution, it appears colorless. Due to its oxidizing properties, hydrogen peroxide is often used as a bleach or cleaning agent. The oxidizing capacity of hydrogen peroxide is so strong that it is considered a highly reactive oxygen species. Hydrogen peroxide is therefore used as a propellant in rocketry.[1] Organisms also naturally produce hydrogen peroxide as a by-product of oxidative metabolism. Consequently, nearly all living things (specifically, all obligate and facultative aerobes) possess enzymes known as catalase peroxidases, which harmlessly and catalytically decompose low concentrations of hydrogen peroxide to water and oxygen.',2005,'Chem. Commun.',8,NULL),(9,9,'Chromium','Chromium is a chemical element which has the symbol Cr and atomic number 24. It is the first element in Group 6. It is a steely-gray, lustrous, hard metal that takes a high polish and has a high melting point. It is also odorless, tasteless, and malleable. The name of the element is derived from the Greek word \"chrōma\" (χρώμα), meaning colour,[2] because many of its compounds are intensely coloured.',2003,'Chem. Commun.',10,NULL),(10,10,'Steel foo bar network','Steel is an alloy made by combining iron and other elements, the most common of these being carbon. When carbon is used, its content in the steel is between 0.2% and 2.1% by weight, depending on the grade. Other alloying elements sometimes used are manganese, chromium, vanadium and tungsten.',2004,'Chem. Commun.',2,NULL);
/*!40000 ALTER TABLE `papers` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-02-27 20:31:27
