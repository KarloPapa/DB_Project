SELECT m.title, g.name
FROM comp373.movies AS m
JOIN comp373.movie_genre AS mg USING (movie_id)
JOIN comp373.genre AS g USING (genre_id)
LIMIT 5;
-- Create view: one row per movie + genre (no movie_id)
CREATE OR REPLACE VIEW comp373.movie_genre_view AS
SELECT 
  m.title,
  g.name AS genre
FROM comp373.movies AS m
JOIN comp373.movie_genre AS mg USING (movie_id)
JOIN comp373.genre AS g USING (genre_id);

-- Check top 5 rows from movie_genre_view
SELECT * 
FROM comp373.movie_genre_view
LIMIT 5;


-- Create aggregated genres per movie view
CREATE OR REPLACE VIEW comp373.movies_with_genres AS
SELECT 
  m.title,
  GROUP_CONCAT(g.name ORDER BY g.name SEPARATOR ', ') AS genres
FROM comp373.movies AS m
JOIN comp373.movie_genre AS mg USING (movie_id)
JOIN comp373.genre AS g USING (genre_id)
GROUP BY m.title;

-- Check top 5 rows from movies_with_genres
SELECT * 
FROM comp373.movies_with_genres
LIMIT 5;
