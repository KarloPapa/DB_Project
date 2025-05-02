import streamlit as st
import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host='comp373.cianci.io',
        port=3306,
        user='kpapa',
        password='firm-limited-eye',
        database='comp373'
    )

def login_sidebar():
    st.sidebar.title("👤 User Login")
    username = st.sidebar.text_input("Username", value=st.session_state.get("username", ""))
    
    if username:
        if "user_id" not in st.session_state or st.session_state.get("username") != username:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT IGNORE INTO users (username) VALUES (%s)", (username,))
            conn.commit()
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            user_id = cursor.fetchone()[0]
            conn.close()

            st.session_state["username"] = username
            st.session_state["user_id"] = user_id
            st.sidebar.success(f"Logged in as {username}")
        else:
            st.sidebar.success(f"Logged in as {username}")
    else:
        st.sidebar.warning("Login to use features")
        st.session_state["user_id"] = None
        st.session_state["username"] = ""
