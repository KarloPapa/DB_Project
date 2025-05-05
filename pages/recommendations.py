import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
from login import login_sidebar, connect_db

# Login
login_sidebar()
user_id = st.session_state.get("user_id")
username = st.session_state.get("username")

# Sidebar UI
st.sidebar.markdown("---")
if username:
    st.sidebar.success(f"✅ Logged in as `{username}`")
else:
    st.sidebar.warning("Login to personalize recommendations")

# Load and preprocess movie data
@st.cache_data
def load_movie_profiles():
    conn = connect_db()
    df = pd.read_sql("""
        SELECT m.movie_id, m.title, m.overview,
               GROUP_CONCAT(DISTINCT g.name) AS genres,
               GROUP_CONCAT(DISTINCT c.name) AS companies
        FROM movies m
        LEFT JOIN movie_genre mg ON m.movie_id = mg.movie_id
        LEFT JOIN genre g ON mg.genre_id = g.genre_id
        LEFT JOIN movie_company mc ON m.movie_id = mc.movie_id
        LEFT JOIN company c ON mc.company_id = c.company_id
        GROUP BY m.movie_id
    """, conn)
    conn.close()
    df['tags'] = (df['genres'].fillna('') + ' ' +
                  df['companies'].fillna('') + ' ' +
                  df['overview'].fillna(''))
    return df

# TF-IDF helper
def get_recommendations(df, tfidf_matrix, title, top_n=10):
    idx = df[df['title'] == title].index
    if idx.empty:
        return pd.DataFrame()
    cosine_sim = cosine_similarity(tfidf_matrix[idx[0]], tfidf_matrix).flatten()
    scores = cosine_sim.argsort()[-(top_n+1):-1][::-1]
    return df.iloc[scores][['movie_id', 'title', 'genres', 'companies', 'overview']]

# Load data and compute matrix 
df = load_movie_profiles()
tfidf = TfidfVectorizer(stop_words='english')
matrix = tfidf.fit_transform(df['tags'])

# UI Header
st.title("🎯 Movie Recommendations")
st.markdown("Pick a movie you like, and we’ll recommend similar ones.")

# Selection trigger 
selected_title = st.selectbox("🎬 Select a Movie:", df['title'].sort_values().unique())
if st.button("🔍 Recommend"):
    st.session_state["recs_triggered"] = True
    st.session_state["selected_base"] = selected_title

# Handle recommendation logic 
if st.session_state.get("recs_triggered") and st.session_state.get("selected_base"):
    base_title = st.session_state["selected_base"]
    recs = get_recommendations(df, matrix, base_title)

    if not recs.empty:
        # Watchlist stars
        if user_id:
            conn = connect_db()
            watchlist_ids = pd.read_sql(f"""
                SELECT movie_id FROM user_movie_activity
                WHERE user_id = {user_id} AND added_to_watchlist = TRUE
            """, conn)["movie_id"].tolist()
            conn.close()
            recs["watchlist"] = recs["movie_id"].apply(lambda x: "⭐" if x in watchlist_ids else "")
            display_df = recs[["watchlist", "title", "genres", "companies"]]
        else:
            display_df = recs[["title", "genres", "companies"]]

        st.markdown("### 🔁 Similar Movies")
        st.dataframe(display_df.reset_index(drop=True))

        # Overview and interaction
        selected_rec_title = st.selectbox("📘 View details for:", recs["title"], key="select_details")
        selected_row = recs[recs["title"] == selected_rec_title]

        if not selected_row.empty:
            overview_text = selected_row["overview"].values[0]
            selected_movie_id = int(selected_row["movie_id"].values[0])
            st.info(overview_text if overview_text else "No overview available.")

            if user_id:
                key_suffix = f"_{selected_movie_id}"
                st.markdown("### ⭐ Add to Watchlist / Rate")

                add_watchlist = st.checkbox("Add to Watchlist", key=f"add{key_suffix}")
                watched = st.checkbox("Watched", key=f"watched{key_suffix}")
                user_rating = st.slider("Your Rating", 0.0, 10.0, key=f"rating{key_suffix}")

                if st.button("Submit Activity", key=f"submit{key_suffix}"):
                    conn = connect_db()
                    cursor = conn.cursor()

                    cursor.execute("""
                        SELECT added_to_watchlist FROM user_movie_activity 
                        WHERE user_id = %s AND movie_id = %s
                    """, (user_id, selected_movie_id))
                    existing = cursor.fetchone()

                    if existing:
                        keep_watchlist = existing[0] or add_watchlist
                        cursor.execute("""
                            UPDATE user_movie_activity
                            SET 
                                added_to_watchlist = %s,
                                watched = %s,
                                rating = %s,
                                date_watched = CASE WHEN %s THEN CURRENT_TIMESTAMP ELSE date_watched END
                            WHERE user_id = %s AND movie_id = %s
                        """, (
                            keep_watchlist,
                            watched,
                            user_rating,
                            watched,
                            user_id,
                            selected_movie_id
                        ))
                    else:
                        date_watched = datetime.now() if watched else None
                        cursor.execute("""
                            INSERT INTO user_movie_activity 
                            (user_id, movie_id, added_to_watchlist, watched, rating, date_watched)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            user_id,
                            selected_movie_id,
                            add_watchlist,
                            watched,
                            user_rating,
                            date_watched
                        ))

                    conn.commit()
                    conn.close()
                    st.success("✅ Movie updated in your profile!")
    else:
        st.warning("No similar movies found.")
