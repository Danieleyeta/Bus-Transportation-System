# BUS_TRANSPORTATION_MANAGEMENT_SYSTEM
Developed a web page using HTML, CSS, JS, Python -Flask as Frontend and MySQL as Backend, which had Login facility, ticket booking facility, information regarding booking status, buses and customers.

Start MySQL in XAMPP:

Open XAMPP Control Panel.
Start the MySQL service.
Create the Database and Tables:

Use phpMyAdmin (included with XAMPP) to create the bus_transportation_system database.


Create the required tables (users, buses, bookings, contact, signin, admin) in this database.

-- bus_transportation_system.admin definition

CREATE TABLE `admin` (
  `admin_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  PRIMARY KEY (`admin_id`,`user_id`),
  UNIQUE KEY `admin_id_UNIQUE` (`admin_id`),
  UNIQUE KEY `user_id_UNIQUE` (`user_id`),
  CONSTRAINT `admin` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=502 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- bus_transportation_system.bookings definition

CREATE TABLE `bookings` (
  `booking_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `bus_id` int NOT NULL,
  `depart` datetime DEFAULT NULL,
  `bk_from` varchar(45) DEFAULT NULL,
  `bk_to` varchar(45) DEFAULT NULL,
  `time` datetime DEFAULT CURRENT_TIMESTAMP,
  `seat_no` int DEFAULT NULL,
  `payment` varchar(20) DEFAULT NULL,
  `payment_status` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`booking_id`,`bus_id`,`user_id`),
  UNIQUE KEY `booking_id_UNIQUE` (`booking_id`),
  KEY `user_id_idx` (`user_id`),
  KEY `bus_id` (`bus_id`),
  CONSTRAINT `bus_id` FOREIGN KEY (`bus_id`) REFERENCES `buses` (`bus_id`),
  CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=244 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- bus_transportation_system.buses definition

CREATE TABLE `buses` (
  `bus_id` int NOT NULL AUTO_INCREMENT,
  `bus_name` varchar(45) DEFAULT NULL,
  `bus_type` varchar(45) DEFAULT NULL,
  `b_from` varchar(45) DEFAULT NULL,
  `b_to` varchar(45) DEFAULT NULL,
  `fare` decimal(10,2) DEFAULT NULL,
  `seats` int DEFAULT NULL,
  PRIMARY KEY (`bus_id`),
  UNIQUE KEY `bus_id_UNIQUE` (`bus_id`)
) ENGINE=InnoDB AUTO_INCREMENT=316 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- bus_transportation_system.contact definition

CREATE TABLE `contact` (
  `contact_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `email` varchar(45) NOT NULL,
  `phone` varchar(45) NOT NULL,
  `msg` varchar(100) DEFAULT NULL,
  `date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`contact_id`),
  UNIQUE KEY `contact_id_UNIQUE` (`contact_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- bus_transportation_system.signin definition

CREATE TABLE `signin` (
  `signin_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `email` varchar(45) DEFAULT NULL,
  `time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`signin_id`,`user_id`),
  UNIQUE KEY `signin_id_UNIQUE` (`signin_id`),
  KEY `userid_idx` (`user_id`),
  CONSTRAINT `userid` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=94 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- bus_transportation_system.users definition

CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `password` varchar(10) DEFAULT NULL,
  `time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_id_UNIQUE` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=117 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;