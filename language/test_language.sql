-- 1. Check that language table has been populated
SELECT COUNT(*) AS language_count FROM comp373.language;

-- 2. Sample language entries (should include common languages)
SELECT * FROM comp373.language ORDER BY language_name LIMIT 10;

-- 3. Check that movies have been updated with language_id
SELECT COUNT(*) AS movies_with_language_id
FROM comp373.movies
WHERE language_id IS NOT NULL;

-- 4. Join test: confirm we can join movies to language successfully
SELECT m.title, l.language_name, l.language_code
FROM comp373.movies m
JOIN comp373.language l ON m.language_id = l.language_id
LIMIT 10;

-- 5. Foreign key constraint check (will fail if broken)
-- Try inserting an invalid language_id into movies
-- This should throw an error (uncomment to test)
-- INSERT INTO comp373.movies (tmdb_id, title, release_date, original_language, vote_average, vote_count, popularity, overview, budget, revenue, runtime, tagline, language_id)
-- VALUES (9999999, 'Test Movie', '2024-01-01', 'FakeLang', 5.0, 100, 1.0, 'Test overview', 1000, 1000, 100, 'Test tagline', 999);


-- 6. Validate the view works
SELECT * FROM comp373.movies_with_languages LIMIT 5;

-- 7. Check an existing language_id
SELECT * FROM comp373.language LIMIT 1;

INSERT INTO comp373.movies (tmdb_id, title, release_date, original_language, vote_average, vote_count, popularity, overview, budget, revenue, runtime, tagline, language_id)
VALUES (9999998, 'Working Test Movie', '2024-01-01', 'English', 6.5, 200, 2.5, 'This should succeed', 500000, 1200000, 110, 'Valid insert test', 1);

