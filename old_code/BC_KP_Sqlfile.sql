USE comp373;

-- 1. Staging
DROP TABLE IF EXISTS movies_raw;
CREATE TABLE movies_raw (
    Unnamed_0            INT,
    tmdb_id              INT,
    title                VARCHAR(255),
    release_date         DATE,
    genres               TEXT,
    original_language    VARCHAR(10),
    vote_average         DECIMAL(3,1),
    vote_count           INT,
    popularity           DECIMAL(7,2),
    overview             TEXT,
    budget               BIGINT,
    production_companies TEXT,
    revenue              BIGINT,
    runtime              INT,
    tagline              TEXT
) ENGINE=InnoDB;

LOAD DATA LOCAL INFILE '/Users/kpapa/Downloads/DBProject-main/top_1000_popular_movies_tmdb.csv'
INTO TABLE movies_raw
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(Unnamed_0, tmdb_id, title, release_date, genres, original_language,
 vote_average, vote_count, popularity, overview, budget,
 production_companies, revenue, runtime, tagline);

-- 2. Normalized movies
DROP TABLE IF EXISTS movies;
CREATE TABLE movies (
    movie_id            INT AUTO_INCREMENT PRIMARY KEY,
    tmdb_id             INT            NOT NULL UNIQUE,
    title               VARCHAR(255)   NOT NULL,
    release_date        DATE           NOT NULL,
    original_language   VARCHAR(10)    NOT NULL,
    vote_average        DECIMAL(3,1)   NOT NULL CHECK (vote_average BETWEEN 0 AND 10),
    vote_count          INT            NOT NULL CHECK (vote_count >= 0),
    popularity          DECIMAL(7,2)   NOT NULL CHECK (popularity >= 0),
    overview            TEXT,
    budget              BIGINT         NOT NULL CHECK (budget >= 0),
    revenue             BIGINT         NOT NULL CHECK (revenue >= 0),
    runtime             INT            CHECK (runtime >= 0),
    tagline             TEXT,
    INDEX idx_vote_avg  (vote_average),
    INDEX idx_rel_date  (release_date),
    FULLTEXT INDEX ft_overview (overview)
) ENGINE=InnoDB;

INSERT INTO movies (tmdb_id, title, release_date,
                    original_language, vote_average, vote_count,
                    popularity, overview, budget, revenue,
                    runtime, tagline)
SELECT tmdb_id, title, release_date,
       original_language, vote_average, vote_count,
       popularity, overview, budget, revenue,
       runtime, tagline
  FROM movies_raw;

-- 3. Genre dimension
DROP TABLE IF EXISTS genre;
CREATE TABLE genre (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- 4. Junction table
DROP TABLE IF EXISTS movie_genre;
CREATE TABLE movie_genre (
    movie_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genre(genre_id)
) ENGINE=InnoDB;

-- 5. Parse & populate genre names
INSERT IGNORE INTO genre (name)
SELECT DISTINCT jt.genre_name
FROM movies_raw AS mr
CROSS JOIN JSON_TABLE(
    -- fix quoting: single → double
    REPLACE(REPLACE(mr.genres, "'", '"'), '""[', '['),
    '$[*]' COLUMNS (
      genre_name VARCHAR(100) PATH '$'
    )
) AS jt;

-- 6. Populate movie_genre links
INSERT INTO movie_genre (movie_id, genre_id)
SELECT m.movie_id, g.genre_id
FROM movies_raw AS mr
JOIN movies AS m
  ON mr.tmdb_id = m.tmdb_id
CROSS JOIN JSON_TABLE(
    REPLACE(REPLACE(mr.genres, "'", '"'), '""[', '['),
    '$[*]' COLUMNS (
      name VARCHAR(100) PATH '$'
    )
) AS jt
JOIN genre AS g
  ON g.name = jt.name;
