import mysql.connector
import pandas as pd
import ast
from tqdm import tqdm
import time

def connect_db():
    return mysql.connector.connect(
        host='comp373.cianci.io',
        port=3306,
        user='kpapa',
        password='firm-limited-eye',
        database='comp373'
    )

def parse_company_list(raw_str):
    try:
        companies = ast.literal_eval(raw_str)
        if isinstance(companies, list):
            return companies
    except Exception:
        pass
    return []

def populate_movie_company():
    conn = connect_db()
    cursor = conn.cursor()

    print("Loading movies...")
    movies_df = pd.read_sql("SELECT movie_id, tmdb_id FROM movies", conn)

    print("Loading companies...")
    companies_df = pd.read_sql("SELECT company_id, name FROM company", conn)

    print("Loading production companies from raw...")
    raw_df = pd.read_sql("SELECT tmdb_id, production_companies FROM movies_raw", conn)

    # Build lookup maps
    tmdb_to_movie_id = dict(zip(movies_df.tmdb_id, movies_df.movie_id))
    company_name_to_id = dict(zip(companies_df.name, companies_df.company_id))

    # Build (movie_id, company_id) pairs
    links = []
    for _, row in raw_df.iterrows():
        movie_id = tmdb_to_movie_id.get(row.tmdb_id)
        if not movie_id:
            continue

        company_names = parse_company_list(row.production_companies)
        for name in company_names:
            company_id = company_name_to_id.get(name)
            if company_id:
                links.append((movie_id, company_id))

    print(f"Preparing to insert {len(links)} movie-company pairs...")
    insert_query = """
        INSERT IGNORE INTO movie_company (movie_id, company_id)
        VALUES (%s, %s)
    """

    # Chunked insert to avoid deadlocks
    batch_size = 1000
    for i in tqdm(range(0, len(links), batch_size)):
        batch = links[i:i + batch_size]
        try:
            cursor.executemany(insert_query, batch)
            conn.commit()
        except mysql.connector.Error as e:
            print(f"⚠️ Skipping batch {i // batch_size + 1} due to error: {e}")
            conn.rollback()
            time.sleep(1)

    print("Insert complete.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    populate_movie_company()
