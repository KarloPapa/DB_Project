import streamlit as st
import pandas as pd
from login import login_sidebar, connect_db  # ✅ Shared login logic

# --- Login ---
login_sidebar()
user_id = st.session_state.get("user_id")
username = st.session_state.get("username")

# --- UI ---
st.title("📺 Your Watchlist")

st.sidebar.markdown("---")
if username:
    st.sidebar.success(f"✅ Logged in as `{username}`")
else:
    st.sidebar.warning("Login to view your watchlist")

# --- Load user watchlist ---
def load_watchlist(user_id):
    conn = connect_db()
    wl = pd.read_sql(f"""
        SELECT m.movie_id, m.title, 
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
    return wl

# --- Main content ---
if user_id:
    wl = load_watchlist(user_id)
    if wl.empty:
        st.info("Your watchlist is empty.")
    else:
        st.dataframe(wl)
        movie_to_remove = st.selectbox("Select a movie to remove from watchlist", wl['title'].tolist())
        if st.button("Remove Selected Movie"):
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_movie_activity
                SET added_to_watchlist = FALSE
                WHERE user_id = %s AND movie_id = (
                    SELECT movie_id FROM movies WHERE title = %s LIMIT 1
                )
            """, (user_id, movie_to_remove))
            conn.commit()
            conn.close()
            st.success(f"Removed **{movie_to_remove}** from your watchlist.")
            st.rerun()
else:
    st.warning("Please log in to access your watchlist.")
