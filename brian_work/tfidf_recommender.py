import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_tfidf_matrix():
    # Connect to the DB
    conn = mysql.connector.connect(
        host='comp373.cianci.io',
        user='bcuellar',
        password='pour-importance-badly',
        database='comp373',
        port=3306
    )
    cursor = conn.cursor(dictionary=True)
    # Updated query: remove 'id' from the SELECT list
    cursor.execute("SELECT title, overview FROM BC_KP_DatabaseProject")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Create a DataFrame from the data
    df = pd.DataFrame(rows)

    # Build the TF-IDF matrix based on the 'overview' field
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['overview'].fillna(''))
    return df, tfidf_matrix, tfidf

def get_similar_movies(input_movie_title, df, tfidf_matrix, tfidf, top_n=10):
    # Find the index of the movie using the title
    idx_list = df.index[df['title'] == input_movie_title].tolist()
    if not idx_list:
        return pd.DataFrame()  # Return empty DataFrame if not found
    idx = idx_list[0]
    
    # Compute cosine similarity between this movie and all others
    cosine_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    similar_indices = cosine_sim.argsort()[-(top_n+1):-1][::-1]  # Exclude the movie itself
    similar_movies = df.iloc[similar_indices]
    return similar_movies
