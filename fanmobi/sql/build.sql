CREATE SCHEMA `fanmobi` ;

CREATE TABLE `fanmobi`.`users` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NULL,
  `password` VARCHAR(255) NULL,
  `salt` VARCHAR(255) NULL,
  PRIMARY KEY (`ID`),
  UNIQUE INDEX `salt_UNIQUE` (`salt` ASC),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC))
  COMMENT = 'the users of the system.The username will be an email address';


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