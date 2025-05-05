-- Indexes for movie_company (junction table) (already ran)
-- CREATE INDEX idx_mc_company_id ON comp373.movie_company(company_id);
-- CREATE INDEX idx_mc_movie_id ON comp373.movie_company(movie_id);

-- Indexes for movie_genre (junction table) (already ran)
-- CREATE INDEX idx_mg_genre_id ON comp373.movie_genre(genre_id);
-- CREATE INDEX idx_mg_movie_id ON comp373.movie_genre(movie_id);

-- Indexes for movies table (already ran)
-- CREATE INDEX idx_movies_release_date ON comp373.movies(release_date);
-- CREATE INDEX idx_movies_vote_average ON comp373.movies(vote_average);
-- CREATE FULLTEXT INDEX ft_movies_overview ON comp373.movies(overview);

-- Indexes for lookup tables (already ran)
-- CREATE UNIQUE INDEX idx_genre_name ON comp373.genre(name);
-- CREATE UNIQUE INDEX idx_company_name ON comp373.company(name);
-- CREATE UNIQUE INDEX idx_language_name ON comp373.language(language_name);

-- Indexes for users (already ran)
-- CREATE INDEX idx_user_movie ON user_movie_activity(user_id, movie_id);
-- CREATE INDEX idx_rating_filter ON user_movie_activity(rating);

-- ALTER TABLE movies ADD FULLTEXT(title, overview);

