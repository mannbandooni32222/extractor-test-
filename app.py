import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json
from pathlib import Path
import hashlib

# ------------------------------
# PART 1: USER DATABASE HELPERS
# ------------------------------

USER_DB = Path("users.json")

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

def authenticate_user(email, password):
    users = load_users()["users"]
    hashed = hash_password(password)
    
    for user in users:
        if user["email"] == email and user["password"] == hashed:
            return True
    return False

def register_user(email, password):
    users_data = load_users()

    # Check if email already exists
    for u in users_data["users"]:
        if u["email"] == email:
            return False

    users_data["users"].append({
        "email": email,
        "password": hash_password(password),
        "plan": "free"
    })

    save_users(users_data)
    return True


# ------------------------------
# PART 2: LOGIN / SIGNUP UI
# ------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 Login or Signup")

    option = st.radio("Select an option", ["Login", "Signup"])

    if option == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate_user(email, password):
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Incorrect email or password")

    else:  # Signup
        email = st.text_input("Create Email")
        password = st.text_input("Create Password", type="password")

        if st.button("Create Account"):
            if register_user(email, password):
                st.success("Account created! You can now log in.")
            else:
                st.error("Email already exists.")

    st.stop()  # ⛔ STOP the app here until user logs in



# ------------------------------
# PART 3: YOUR EXTRACTOR TOOL
# ------------------------------

st.title("Free Email & Social Media Extractor (MVP Version)")

urls_input = st.text_area("Enter websites (one per line):")

extract_btn = st.button("Extract Information")

def extract_info(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        # Extract only one email
        emails = list(set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", html)))
        email = emails[0] if emails else "Not found"

        insta = soup.find("a", href=re.compile("instagram.com"))
        insta_link = insta["href"] if insta else "Not found"

        fb = soup.find("a", href=re.compile("facebook.com"))
        fb_link = fb["href"] if fb else "Not found"

        return email, insta_link, fb_link

    except:
        return "Error", "Error", "Error"


if extract_btn:
    urls = urls_input.split("\n")
    urls = [u.strip() for u in urls if u.strip()]

    limited_urls = urls[:5]  # LIMIT to 5

    results = []

    for url in limited_urls:
        email, ig, fb = extract_info(url)
        results.append({
            "Website": url,
            "Email (1 Only)": email,
            "Instagram": ig,
            "Facebook": fb
        })

    if len(urls) > 5:
        st.warning("Free version: Only 5 websites allowed.")

    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)
    st.download_button("Download CSV (5 rows max)", csv, "results.csv", "text/csv")
