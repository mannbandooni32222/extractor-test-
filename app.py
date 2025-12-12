import json
from pathlib import Path
import hashlib
import streamlit as st
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

st.title("Email & Social Media Extractor (MVP Version)")

# Input
urls_input = st.text_area("Enter websites (one per line):")

extract_btn = st.button("Extract Information")

def extract_info(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        # Extract only ONE email (first found)
        emails = list(set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", html)))
        email = emails[0] if emails else "Not found"

        # Instagram link
        insta = soup.find("a", href=re.compile("instagram.com"))
        insta_link = insta["href"] if insta else "Not found"

        # Facebook link
        fb = soup.find("a", href=re.compile("facebook.com"))
        fb_link = fb["href"] if fb else "Not found"

        return email, insta_link, fb_link

    except:
        return "Error", "Error", "Error"



if extract_btn:
    urls = urls_input.split("\n")
    urls = [u.strip() for u in urls if u.strip()]  # remove empty lines

    # LIMIT to 5 websites only
    limited_urls = urls[:5]

    results = []

    for url in limited_urls:
        email, ig, fb = extract_info(url)
        results.append({
            "Website": url,
            "Email (1 Only)": email,
            "Instagram": ig,
            "Facebook": fb
        })

    # Warning if user entered more than 5
    if len(urls) > 5:
        st.warning("Free version limit reached. Only the first 5 websites were extracted.")

    # Show results table
    st.subheader("Extracted Results (Max 5) — Free Version")
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)

    # CSV Download (5 rows only)
    csv_data = df.to_csv(index=False)
    st.download_button("Download CSV (5 rows)", csv_data, "results.csv", "text/csv")

    # No history — nothing is stored
    st.info("Note: This free version does not save history. All results are temporary.")



# Hide Streamlit top-right menu + footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}     /* Hides hamburger menu */
    header {visibility: hidden;}        /* Hides top header */
    footer {visibility: hidden;}        /* Hides footer */
    .stDeployButton {display: none;}    /* Hides deploy button */
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)




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
    
    # Check if email exists
    for u in users_data["users"]:
        if u["email"] == email:
            return False  # email exists

    users_data["users"].append({
        "email": email,
        "password": hash_password(password),
        "plan": "free"   # free plan by default
    })

    save_users(users_data)
    return True

