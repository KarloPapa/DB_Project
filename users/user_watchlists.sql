-- Drop existing tables to avoid conflicts
DROP TABLE IF EXISTS user_movie_activity;
DROP TABLE IF EXISTS users;

-- 1. Users table (for login, rating & personalization)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Watchlist with ratings (track which users added/rated which movies)
CREATE TABLE user_movie_activity (
    user_id INT,
    movie_id INT,
    added_to_watchlist BOOLEAN DEFAULT FALSE,
    watched BOOLEAN DEFAULT FALSE,
    rating DECIMAL(2,1) CHECK (rating BETWEEN 0 AND 10),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_watched TIMESTAMP NULL, -- ✅ New column to track when the user watched the movie
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);
