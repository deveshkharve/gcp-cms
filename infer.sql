DROP TABLE IF EXISTS `project`;

CREATE TABLE IF NOT EXISTS `project` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `description` text NOT NULL,
  `user_id` int(11) NOT NULL,	
  `library` varchar(255) DEFAULT NULL,
  `path` varchar(255) DEFAULT NULL,
  `package` varchar(255) DEFAULT NULL,
  `createdat` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `modifiedat` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

DROP TABLE IF EXISTS `users`;

CREATE TABLE IF NOT EXISTS `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `companyname` varchar(255) DEFAULT NULL,
  `designation` int(45) DEFAULT NULL,
  `package` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `country` varchar(255) DEFAULT NULL,
  `address_line1` varchar(255) DEFAULT NULL,
  `address_line2` varchar(255) DEFAULT NULL,
  `pin` varchar(45) DEFAULT NULL,
  `createdat` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `modifiedat` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY (`email`)
); 


