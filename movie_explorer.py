import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
from login import login_sidebar, connect_db  # ⬅️ import login logic

# UI
st.title("🎬 Movie Explorer")

# Login
login_sidebar()
user_id = st.session_state.get("user_id")
username = st.session_state.get("username")

# Fetch dropdown/filter options
@st.cache_data
def get_filter_options():
    conn = connect_db()
    genres = pd.read_sql("SELECT DISTINCT name FROM genre ORDER BY name", conn)['name'].tolist()
    companies = pd.read_sql("SELECT DISTINCT name FROM company ORDER BY name", conn)['name'].tolist()
    years = pd.read_sql("SELECT DISTINCT YEAR(release_date) AS year FROM movies ORDER BY year DESC", conn)['year'].dropna().astype(int).tolist()
    languages = pd.read_sql("SELECT DISTINCT language_name FROM language ORDER BY language_name", conn)['language_name'].tolist()
    conn.close()
    return genres, companies, years, languages

# Filters
genres, companies, years, languages = get_filter_options()
genre = st.selectbox("Filter by Genre", ["(Any)"] + genres)
company = st.selectbox("Filter by Company", ["(Any)"] + companies)
year = st.selectbox("Filter by Year", ["(Any)"] + [str(y) for y in years])
language = st.selectbox("Filter by Language", ["(Any)"] + languages)
min_rating = st.slider("Minimum Rating", 0.0, 10.0, 0.0)
min_popularity = st.slider("Minimum Popularity", 0, 10000, 0)
keyword = st.text_input("Search by keywords in description (overview)", "")

# Reset form state on new search
if "reset_flag" not in st.session_state:
    st.session_state.reset_flag = False

def reset_form():
    st.session_state.add_watchlist = False
    st.session_state.watched = False
    st.session_state.user_rating = 0.0
    st.session_state.reset_flag = True

# Build SQL Query
conditions = [f"m.vote_average >= {min_rating}", f"m.popularity >= {min_popularity}"]
if genre != "(Any)":
    conditions.append(f"g.name = '{genre}'")
if company != "(Any)":
    conditions.append(f"c.name = '{company}'")
if year != "(Any)":
    conditions.append(f"YEAR(m.release_date) = {int(year)}")
if language != "(Any)":
    conditions.append(f"l.language_name = '{language}'")
if keyword:
    conditions.append(f"MATCH(m.title, m.overview) AGAINST ('{keyword}' IN NATURAL LANGUAGE MODE)")

where_clause = " AND ".join(conditions)
order_clause = f"ORDER BY MATCH(m.overview) AGAINST ('{keyword}' IN NATURAL LANGUAGE MODE) DESC" if keyword else "ORDER BY m.popularity DESC"

query = f"""
SELECT DISTINCT m.movie_id, m.title, m.release_date, m.vote_average, m.popularity, m.overview
FROM movies m
LEFT JOIN movie_genre mg USING (movie_id)
LEFT JOIN genre g USING (genre_id)
LEFT JOIN movie_company mc USING (movie_id)
LEFT JOIN company c USING (company_id)
LEFT JOIN language l ON m.language_id = l.language_id
WHERE {where_clause}
{order_clause}
LIMIT 100;
"""

# Run query + store results
if st.button("Search"):
    reset_form()
    conn = connect_db()
    df = pd.read_sql(query, conn)

    if user_id:
        watchlist_ids = pd.read_sql(f"""
            SELECT movie_id FROM user_movie_activity
            WHERE user_id = {user_id} AND added_to_watchlist = TRUE
        """, conn)["movie_id"].tolist()

        df["watchlist"] = df["movie_id"].apply(lambda x: "⭐" if x in watchlist_ids else "")
    else:
        df["watchlist"] = ""

    conn.close()
    st.session_state['last_results'] = df

# Show results if we have them 
if 'last_results' in st.session_state:
    df = st.session_state['last_results']
    st.write(f"### 🎉 Found {len(df)} matching movies")
    st.dataframe(df[["watchlist", "title", "release_date", "vote_average", "popularity"]])

    st.markdown("### 📘 View Overview for a Movie")
    selected_title = st.selectbox("Select a movie", df["title"])
    overview_row = df[df["title"] == selected_title]
    if not overview_row.empty:
        overview_text = overview_row["overview"].values[0]
        st.info(overview_text if overview_text else "No overview available.")
    else:
        st.warning("Overview not found for selected movie.")

    # Watchlist & rating features
    if user_id:
        selected_row = df[df["title"] == selected_title]
        if not selected_row.empty:
            selected_movie_id = int(selected_row["movie_id"].values[0])

            st.markdown("### ⭐ Add to Watchlist / Rate")
            add_watchlist = st.checkbox("Add to Watchlist", value=st.session_state.get("add_watchlist", False), key="add_watchlist")
            watched = st.checkbox("Watched", value=st.session_state.get("watched", False), key="watched")
            user_rating = st.slider("Your Rating", 0.0, 10.0, st.session_state.get("user_rating", 0.0), key="user_rating")

            if st.button("Submit Activity"):
                conn = connect_db()
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT added_to_watchlist FROM user_movie_activity 
                    WHERE user_id = %s AND movie_id = %s
                """, (user_id, selected_movie_id))
                existing = cursor.fetchone()

                if existing:
                    keep_watchlist = existing[0] or add_watchlist
                    query = """
                        UPDATE user_movie_activity
                        SET 
                            added_to_watchlist = %s,
                            watched = %s,
                            rating = %s,
                            date_watched = CASE WHEN %s THEN CURRENT_TIMESTAMP ELSE date_watched END
                        WHERE user_id = %s AND movie_id = %s
                    """
                    cursor.execute(query, (
                        keep_watchlist,
                        watched,
                        user_rating,
                        watched,
                        user_id,
                        selected_movie_id
                    ))
                else:
                    date_watched = datetime.now() if watched else None
                    query = """
                        INSERT INTO user_movie_activity 
                        (user_id, movie_id, added_to_watchlist, watched, rating, date_watched)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (
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

                # Show user's watchlist at the bottom
                conn = connect_db()
                wl = pd.read_sql(f"""
                    SELECT m.title, 
                           CASE WHEN uma.watched THEN '✅ Watched' ELSE '❌ Not Watched' END AS watched,
                           uma.rating, 
                           uma.date_watched,
                           uma.added_at
                    FROM user_movie_activity uma
                    JOIN movies m ON uma.movie_id = m.movie_id
                    WHERE uma.user_id = {user_id} AND uma.added_to_watchlist = TRUE
                    ORDER BY uma.added_at DESC
                """, conn)
                conn.close()
                st.markdown("### 📺 Your Watchlist")
                st.dataframe(wl if not wl.empty else pd.DataFrame({'Watchlist': ['Nothing added yet']}))
