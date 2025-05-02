-- 0) Sanity: initial staging count
SELECT 
  COUNT(*) AS raw_row_count 
FROM `comp373`.`movies_raw`;
SELECT * FROM `comp373`.`movies_raw` LIMIT 10;

-- 1a) Drop old tables
DROP TABLE IF EXISTS `comp373`.`movie_genre`;
DROP TABLE IF EXISTS `comp373`.`genre`;
DROP TABLE IF EXISTS `comp373`.`movies`;

-- 1a-check: ensure drops succeeded for movies
SELECT 
  IF(
    (SELECT COUNT(*) 
       FROM information_schema.tables 
      WHERE table_schema='comp373' 
        AND table_name='movies'
    ) = 0,
    'movies dropped',
    'ERROR: movies still exists'
  ) AS movies_drop_check;

-- 1b) Create movies table
CREATE TABLE `comp373`.`movies` (
  `movie_id`          INT AUTO_INCREMENT PRIMARY KEY,
  `tmdb_id`           INT            NOT NULL UNIQUE,
  `title`             VARCHAR(255)   NOT NULL,
  `release_date`      DATE           NOT NULL,
  `original_language` VARCHAR(10)    NOT NULL,
  `vote_average`      DECIMAL(3,1)   NOT NULL CHECK (`vote_average` BETWEEN 0 AND 10),
  `vote_count`        INT            NOT NULL CHECK (`vote_count` >= 0),
  `popularity`        DECIMAL(7,2)   NOT NULL CHECK (`popularity` >= 0),
  `overview`          TEXT,
  `budget`            BIGINT         NOT NULL CHECK (`budget` >= 0),
  `revenue`           BIGINT         NOT NULL CHECK (`revenue` >= 0),
  `runtime`           INT            CHECK (`runtime` >= 0),
  `tagline`           TEXT,
  INDEX `idx_vote_avg`  (`vote_average`),
  INDEX `idx_rel_date`  (`release_date`),
  FULLTEXT INDEX `ft_overview` (`overview`)
) ENGINE=InnoDB;

-- 1b-check: confirm creation of movies
SELECT 
  IF(
    (SELECT COUNT(*) 
       FROM information_schema.tables 
      WHERE table_schema='comp373' 
        AND table_name='movies'
    ) = 1,
    'movies created',
    'ERROR: movies creation failed'
  ) AS movies_create_check;

-- 1c) Populate movies from staging
INSERT INTO `comp373`.`movies` (
    `tmdb_id`, `title`, `release_date`, `original_language`,
    `vote_average`, `vote_count`, `popularity`, `overview`,
    `budget`, `revenue`, `runtime`, `tagline`
)
SELECT
    `tmdb_id`, `title`, `release_date`, `original_language`,
    `vote_average`, `vote_count`, `popularity`, `overview`,
    `budget`, `revenue`, `runtime`, `tagline`
  FROM `comp373`.`movies_raw`;

-- 1c-check: rows inserted and totals
SELECT 
  ROW_COUNT()               AS inserted_into_movies,
  (SELECT COUNT(*) FROM `comp373`.`movies_raw`) AS raw_total,
  (SELECT COUNT(*) FROM `comp373`.`movies`)    AS movies_total;

-- 1d) Final movies check
SELECT 
  COUNT(*) AS final_movie_count 
FROM `comp373`.`movies`;

-- 2a) Create genre lookup table
CREATE TABLE `comp373`.`genre` (
  `genre_id` INT AUTO_INCREMENT PRIMARY KEY,
  `name`     VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- 2a-check: confirm creation of genre
SELECT 
  IF(
    (SELECT COUNT(*) 
       FROM information_schema.tables 
      WHERE table_schema='comp373' 
        AND table_name='genre'
    ) = 1,
    'genre created',
    'ERROR: genre creation failed'
  ) AS genre_create_check;

-- 2b) Populate genre lookup from staging JSON
INSERT IGNORE INTO `comp373`.`genre` (`name`)
SELECT DISTINCT jt.genre_name
FROM `comp373`.`movies_raw` AS mr
CROSS JOIN JSON_TABLE(
  REPLACE(REPLACE(mr.genres, '''', '"'), '""[', '['),
  '$[*]' COLUMNS (
    genre_name VARCHAR(100)
      CHARACTER SET utf8mb4
      COLLATE utf8mb4_general_ci
      PATH '$'
  )
) AS jt;

-- 2b-check: rows inserted into genre
SELECT 
  ROW_COUNT()               AS inserted_into_genre,
  (SELECT COUNT(*) FROM `comp373`.`genre`) AS genre_total;

-- 3a) Create movie_genre junction table
CREATE TABLE `comp373`.`movie_genre` (
  `movie_id` INT NOT NULL,
  `genre_id` INT NOT NULL,
  PRIMARY KEY (`movie_id`,`genre_id`),
  FOREIGN KEY (`movie_id`) REFERENCES `comp373`.`movies` (`movie_id`),
  FOREIGN KEY (`genre_id`) REFERENCES `comp373`.`genre`  (`genre_id`)
) ENGINE=InnoDB;

-- 3a-check: confirm creation of movie_genre
SELECT 
  IF(
    (SELECT COUNT(*) 
       FROM information_schema.tables 
      WHERE table_schema='comp373' 
        AND table_name='movie_genre'
    ) = 1,
    'movie_genre created',
    'ERROR: movie_genre creation failed'
  ) AS movie_genre_create_check;

-- 3b) Populate movie↔genre junction
INSERT IGNORE INTO `comp373`.`movie_genre` (`movie_id`, `genre_id`)
SELECT m.movie_id
     , g.genre_id
FROM `comp373`.`movies_raw` AS mr
JOIN `comp373`.`movies` AS m
  ON mr.tmdb_id = m.tmdb_id
CROSS JOIN JSON_TABLE(
  REPLACE(REPLACE(mr.genres, '''', '"'), '""[', '['),
  '$[*]' COLUMNS (
    name VARCHAR(100)
      CHARACTER SET utf8mb4
      COLLATE utf8mb4_general_ci
      PATH '$'
  )
) AS jt
JOIN `comp373`.`genre` AS g
  ON g.name = jt.name;

-- 3b-check: rows inserted into movie_genre
SELECT 
  ROW_COUNT()                     AS inserted_into_movie_genre,
  (SELECT COUNT(*) FROM `comp373`.`movie_genre`) AS junction_total;

-- Final sanity checks

SELECT COUNT(*) AS genre_count 
  FROM `comp373`.`genre`;

SELECT * FROM `comp373`.`genre` LIMIT 10;

SELECT COUNT(*) AS link_count 
  FROM `comp373`.`movie_genre`;

SELECT * FROM `comp373`.`movie_genre` LIMIT 10;