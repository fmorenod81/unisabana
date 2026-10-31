CREATE DATABASE `appdemo`;
  USE `appdemo`;
  CREATE TABLE `demodata` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100),
  `notes` TEXT,
  `timestamp` TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY (`name`)
  );

  CREATE TABLE `demodata_erase_log` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `timestamp` TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY (`timestamp`)
  );
CREATE USER 'appdemo'@'localhost' IDENTIFIED BY 'appdemo1';
GRANT ALL PRIVILEGES ON appdemo.demodata TO 'appdemo'@'localhost';
FLUSH PRIVILEGES;