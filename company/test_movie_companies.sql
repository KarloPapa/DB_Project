-- 1. Total count of rows
SELECT COUNT(*) AS total_movie_company_links
FROM comp373.movie_company;

-- 2. Number of distinct movies linked to at least one company
SELECT COUNT(DISTINCT movie_id) AS movies_with_companies
FROM comp373.movie_company;

-- 3. Top 10 companies with the most movie links
SELECT c.name, COUNT(*) AS num_movies
FROM comp373.movie_company mc
JOIN comp373.company c ON mc.company_id = c.company_id
GROUP BY c.name
ORDER BY num_movies DESC
LIMIT 10;

-- 4. Sample movie-company links (first 10 rows)
SELECT mc.movie_id, m.title, c.name AS company
FROM comp373.movie_company mc
JOIN comp373.movies m ON mc.movie_id = m.movie_id
JOIN comp373.company c ON mc.company_id = c.company_id
LIMIT 10;
