-- 1) Count NULL / empty / empty-list rows in staging
SELECT
  COUNT(*)                          AS total_rows,
  SUM(genres IS NULL)              AS null_count,
  SUM(genres = '')                  AS empty_string_count,
  SUM(genres = '[]')                AS empty_list_count
FROM `comp373`.`movies_raw`;

-- 2) Peek at up to 20 distinct raw genre values
SELECT DISTINCT `genres` 
FROM `comp373`.`movies_raw`
LIMIT 20;

-- 3) Find rows that still aren’t valid JSON after our REPLACE fixes
SELECT
  `genres` AS raw_genres,
  JSON_VALID(
    REPLACE(
      REPLACE(`genres`, '''', '"'),
      '""[', '['
    )
  ) AS is_valid_json
FROM `comp373`.`movies_raw`
WHERE JSON_VALID(
    REPLACE(
      REPLACE(`genres`, '''', '"'),
      '""[', '['
    )
  ) = 0
LIMIT 20;

-- 4) Spot rows with uneven quote counts (might indicate stray/mismatched quotes)
SELECT
  `genres`,
  (CHAR_LENGTH(`genres`) - CHAR_LENGTH(REPLACE(`genres`, '''', ''))) AS single_quote_count,
  (CHAR_LENGTH(`genres`) - CHAR_LENGTH(REPLACE(`genres`, '"', '')))  AS double_quote_count
FROM `comp373`.`movies_raw`
WHERE
  ((CHAR_LENGTH(`genres`) - CHAR_LENGTH(REPLACE(`genres`, '''', ''))) % 2) != 0
  OR
  ((CHAR_LENGTH(`genres`) - CHAR_LENGTH(REPLACE(`genres`, '"', '')))  % 2) != 0
LIMIT 20;
