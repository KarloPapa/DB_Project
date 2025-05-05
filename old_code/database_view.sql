USE comp373;

-- 1. One row per movie+genre
DROP VIEW IF EXISTS movie_genre_view;
CREATE VIEW movie_genre_view AS
SELECT
  m.movie_id,
  m.title,
  g.genre_id,
  g.name AS genre_name
FROM movies m
JOIN movie_genre mg USING (movie_id)
JOIN genre       g  USING (genre_id);

-- 2. Aggregated genres per movie
DROP VIEW IF EXISTS movies_with_genres;
CREATE VIEW movies_with_genres AS
SELECT
  m.movie_id,
  m.title,
  GROUP_CONCAT(g.name ORDER BY g.name SEPARATOR ', ') AS genres
FROM movies m
JOIN movie_genre mg USING (movie_id)
JOIN genre       g  USING (genre_id)
GROUP BY m.movie_id, m.title;
