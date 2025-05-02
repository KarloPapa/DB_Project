-- Test: basic join to confirm structure before creating views
SELECT m.title, c.name
FROM comp373.movies AS m
JOIN comp373.movie_company AS mc USING (movie_id)
JOIN comp373.company AS c USING (company_id)
LIMIT 5;

-- Create view: one row per movie + company
CREATE OR REPLACE VIEW comp373.movie_company_view AS
SELECT 
  m.title,
  c.name AS company
FROM comp373.movies AS m
JOIN comp373.movie_company AS mc USING (movie_id)
JOIN comp373.company AS c USING (company_id);

-- Check: Top 5 rows from movie_company_view
SELECT * 
FROM comp373.movie_company_view
LIMIT 5;

-- Create view: aggregated companies per movie
CREATE OR REPLACE VIEW comp373.movies_with_companies AS
SELECT 
  m.title,
  GROUP_CONCAT(c.name ORDER BY c.name SEPARATOR ', ') AS companies
FROM comp373.movies AS m
JOIN comp373.movie_company AS mc USING (movie_id)
JOIN comp373.company AS c USING (company_id)
GROUP BY m.title;

-- Check: Top 5 rows from movies_with_companies
SELECT * 
FROM comp373.movies_with_companies
LIMIT 5;

SHOW INDEXES FROM comp373.movie_company;

