create database AI
use AI
CREATE TABLE movies (
  id INT NOT NULL AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  mpaa_rating VARCHAR(10),
  budget int,
  gross int,
  release_date DATE,
  genre VARCHAR(255),
  runtime INT,
  rating FLOAT,
  rating_count INT,
  PRIMARY KEY (id)
);
