CREATE SCHEMA `fanmobi` ;

CREATE TABLE `fanmobi`.`users`(
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(45) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `salt` varchar(255) DEFAULT NULL,
  `facebook_id` varchar(45) DEFAULT NULL,
  `twitter_id` varchar(45) DEFAULT NULL,
  `cookie` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `salt_UNIQUE` (`salt`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `facebook_id_UNIQUE` (`facebook_id`),
  UNIQUE KEY `twitter_id_UNIQUE` (`twitter_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8 COMMENT='the users of the system.  The username will be an email address';



CREATE TABLE `fanmobi`.`user_roles` (
  `user_id` INT NOT NULL,
  `role` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`user_id`, `role`),
  CONSTRAINT `users_fk`
  FOREIGN KEY (`user_id`)
  REFERENCES `fanmobi`.`users` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
  COMMENT = 'users and their associated roles' ;

CREATE TABLE `fanmobi`.`user_connections` (
  `user` INT NOT NULL,
  `connected_to` INT NOT NULL,
  INDEX `user_fk_idx` (`user` ASC),
  INDEX `connected_to_idx` (`connected_to` ASC),
  CONSTRAINT `user_fk`
  FOREIGN KEY (`user`)
  REFERENCES `fanmobi`.`users` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
  COMMENT = 'Represents the connections a user has, as a graph' ;

CREATE TABLE `fanmobi`.`artist_profiles` (
  `artist_id` INT NOT NULL,
  `name` VARCHAR(255) NULL,
  `thumbnail` VARCHAR(4000) NULL,
  `allows_messages` VARCHAR(5) NULL DEFAULT 'true',
  PRIMARY KEY (`artist_id`),
  CONSTRAINT `artist_id_fk`
  FOREIGN KEY (`artist_id`)
  REFERENCES `fanmobi`.`users` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
  COMMENT = 'Represents the profile of an artist';
