import mysql.connector
import pandas as pd

def load_movies_raw(csv_path: str):
    """Load cleaned CSV into the movies_raw staging table."""
    conn = mysql.connector.connect(
        host='comp373.cianci.io',
        port=3306,
        user='kpapa',
        password='firm-limited-eye',
        database='comp373'
    )
    cursor = conn.cursor()

    # Drop and create the staging table
    cursor.execute("DROP TABLE IF EXISTS movies_raw;")
    cursor.execute("""
    CREATE TABLE movies_raw (
      Unnamed_0 INT,
      tmdb_id INT,
      title VARCHAR(255),
      release_date DATE,
      genres TEXT,
      original_language VARCHAR(10),
      vote_average DECIMAL(3,1),
      vote_count INT,
      popularity DECIMAL(7,2),
      overview TEXT,
      budget BIGINT,
      production_companies TEXT,
      revenue BIGINT,
      runtime INT,
      tagline TEXT
    ) ENGINE=InnoDB;
    """)

    # Load cleaned CSV with pandas
    df = pd.read_csv(csv_path)

    # Prepare cleaned rows with NaN → None
    cleaned_rows = [
        tuple(None if pd.isna(x) else x for x in row)
        for row in df.itertuples(index=False)
    ]

    # Insert all rows at once
    insert_query = """
    INSERT INTO movies_raw (
        Unnamed_0, tmdb_id, title, release_date, genres,
        original_language, vote_average, vote_count, popularity,
        overview, budget, production_companies, revenue, runtime, tagline
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, cleaned_rows)
    conn.commit()

    # Confirm row count
    cursor.execute("SELECT COUNT(*) FROM movies_raw;")
    count = cursor.fetchone()[0]
    print(f"Loaded {count} rows into movies_raw")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    csv_path = '/Users/kpapa/Downloads/DBProject-main/karlo_work/movies_cleaned.csv'
    load_movies_raw(csv_path)
