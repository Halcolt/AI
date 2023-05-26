create database AI
use AI
CREATE TABLE movies (
  id INT NOT NULL AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  MPAA_Rating varchar(255),
  budget int,
  gross int,
  release_date DATE,
  genre VARCHAR(255),
  runtime INT,
  rating FLOAT,
  rating_count INT,
  profit INT,
  PRIMARY KEY (id)
);

drop database AI
select * from movies
