import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json
import hashlib
from pathlib import Path

# ------------------------------
# CONFIG
# ------------------------------

USER_DB = Path("users.json")

# ------------------------------
# HELPERS
# ------------------------------

def load_users():
    if USER_DB.exists():
        with open(USER_DB, "r") as f:
            return json.load(f)
    return {"users": []}

def save_users(data):
    with open(USER_DB, "w") as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(email, password):
    users = load_users()["users"]
    hashed = hash_password(password)
    for u in users:
        if u["email"] == email and u["password"] == hashed:
            return True
    return False

def register(email, password):
    data = load_users()
    for u in data["users"]:
        if u["email"] == email:
            return False

    data["users"].append({
        "email": email,
        "password": hash_password(password),
        "plan": "free"
    })
    save_users(data)
    return True

# ------------------------------
# SESSION
# ------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------------------
# LOGIN / SIGNUP UI
# ------------------------------

if not st.session_state.logged_in:
    st.title("🔐 Login or Signup")

    choice = st.radio("Select option", ["Login", "Signup"])

    if choice == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(email, password):
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success("Logged in successfully")
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        email = st.text_input("Create Email")
        password = st.text_input("Create Password", type="password")

        if st.button("Create Account"):
            if register(email, password):
                st.success("Account created. Please login.")
            else:
                st.error("Email already exists")

    st.stop()

# ------------------------------
# LOGOUT
# ------------------------------

st.sidebar.success("Logged in")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ------------------------------
# EXTRACTOR
# ------------------------------

st.title("Free Email & Social Media Extractor (MVP)")

urls_input = st.text_area("Enter websites (one per line)")
extract_btn = st.button("Extract")

def extract_info(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        emails = re.findall(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            html
        )
        email = emails[0] if emails else "Not found"

        insta = soup.find("a", href=re.compile("instagram.com"))
        fb = soup.find("a", href=re.compile("facebook.com"))

        return (
            email,
            insta["href"] if insta else "Not found",
            fb["href"] if fb else "Not found"
        )
    except:
        return "Error", "Error", "Error"

if extract_btn:
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
    urls = urls[:5]  # FREE LIMIT

    results = []

    for url in urls:
        email, ig, fb = extract_info(url)
        results.append({
            "Website": url,
            "Email (1 only)": email,
            "Instagram": ig,
            "Facebook": fb
        })

    if len(urls_input.split("\n")) > 5:
        st.warning("Free plan allows only 5 websites.")

    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)
    st.download_button(
        "Download CSV (5 rows)",
        csv,
        "results.csv",
        "text/csv"
    )

# ------------------------------
# HIDE STREAMLIT UI
# ------------------------------

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

