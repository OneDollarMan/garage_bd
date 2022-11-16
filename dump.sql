CREATE SCHEMA garage;
USE garage;
CREATE TABLE `car` (`idcar` int NOT NULL AUTO_INCREMENT, `brand` varchar(45) NOT NULL, `model` varchar(45) NOT NULL, `plate` varchar(45) NOT NULL, `year` year NOT NULL, PRIMARY KEY (`idcar`)) ENGINE=InnoDB;
CREATE TABLE `gas` (`idgas` int NOT NULL AUTO_INCREMENT, `brand` varchar(45) NOT NULL, `octane` varchar(45) NOT NULL, `remain` int DEFAULT '0', PRIMARY KEY (`idgas`)) ENGINE=InnoDB;
CREATE TABLE `station` (`idstation` int NOT NULL AUTO_INCREMENT, `name` varchar(45) NOT NULL, `address` varchar(45) NOT NULL, PRIMARY KEY (`idstation`)) ENGINE=InnoDB;
CREATE TABLE `transportation` (`idtransportation` int NOT NULL AUTO_INCREMENT, `date` datetime NOT NULL, `driver` int NOT NULL, `gas` int NOT NULL, `station` int NOT NULL, `gas_amount` int NOT NULL, `status` int NOT NULL DEFAULT '0', PRIMARY KEY (`idtransportation`), KEY `driver_idx` (`driver`), KEY `gas_idx` (`gas`)) ENGINE=InnoDB;
CREATE TABLE `user` (`iduser` int NOT NULL AUTO_INCREMENT, `username` varchar(45) NOT NULL, `fio` varchar(120) NOT NULL, `password` varchar(45) NOT NULL, `role` int NOT NULL DEFAULT '0', `car` int DEFAULT NULL, PRIMARY KEY (`iduser`)) ENGINE=InnoDB;
CREATE TABLE `var` (`idvar` int NOT NULL, `text` varchar(45) NOT NULL, PRIMARY KEY (`idvar`)) ENGINE=InnoDB;
INSERT INTO `var` VALUES (0, '�����'), (1, '� ����'), (2, '��������');
INSERT INTO `user` VALUES (1,'root','root','63a9f0ea7bb98050796b649e85481845',2,Null);