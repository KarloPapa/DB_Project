-- 1. Drop old table if it exists
DROP TABLE IF EXISTS comp373.language;

-- 2. Create a normalized language lookup table
CREATE TABLE comp373.language (
  language_id INT AUTO_INCREMENT PRIMARY KEY,
  language_name VARCHAR(100) NOT NULL UNIQUE,
  language_code VARCHAR(10),        
  region VARCHAR(50),               
  family VARCHAR(50)                
) ENGINE=InnoDB;

-- 3. Populate language table with distinct entries from movies table
INSERT IGNORE INTO comp373.language (language_name)
SELECT DISTINCT original_language
FROM comp373.movies
WHERE original_language IS NOT NULL;

-- 4. Add `language_id` to movies
ALTER TABLE comp373.movies
ADD COLUMN language_id INT NULL;

-- 5. Update it using a join on language name
UPDATE comp373.movies AS m
JOIN comp373.language AS l
  ON m.original_language = l.language_name
SET m.language_id = l.language_id;

-- 6. Add a foreign key constraint
ALTER TABLE comp373.movies
ADD CONSTRAINT fk_language_id FOREIGN KEY (language_id)
REFERENCES comp373.language(language_id);

-- 7. Create a view to show movie titles with full language metadata
CREATE OR REPLACE VIEW comp373.movies_with_languages AS
SELECT 
  m.title,
  l.language_name,
  l.language_code,
  l.region,
  l.family
FROM comp373.movies m
LEFT JOIN comp373.language l ON m.language_id = l.language_id;
