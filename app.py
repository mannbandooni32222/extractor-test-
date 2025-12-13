import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# ------------------------------
# FIREBASE CONFIG
# ------------------------------

firebase_config = {
    "apiKey": st.secrets["firebase"]["apiKey"],
    "authDomain": st.secrets["firebase"]["authDomain"],
    "projectId": st.secrets["firebase"]["projectId"],
    "storageBucket": st.secrets["firebase"]["storageBucket"],
    "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
    "appId": st.secrets["firebase"]["appId"],
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# ------------------------------
# SESSION STATE
# ------------------------------

if "user" not in st.session_state:
    st.session_state.user = None

# ------------------------------
# LOGIN / SIGNUP UI (FIREBASE)
# ------------------------------

if not st.session_state.user:

    st.title("🔐 Login to Continue")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.user = user
                st.success("Logged in successfully")
                st.rerun()
            except:
                st.error("Invalid email or password")

    with tab2:
        email = st.text_input("Create Email")
        password = st.text_input("Create Password", type="password")

        if st.button("Create Account"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("Account created. Please login.")
            except:
                st.error("Account already exists or weak password")

    st.markdown("---")
    st.info("Google Login will be added after deployment")
    st.stop()

# ------------------------------
# EXTRACTOR TOOL (UNCHANGED)
# ------------------------------

st.title("Free Email & Social Media Extractor (MVP)")

urls_input = st.text_area("Enter websites (one per line)")
extract_btn = st.button("Extract Information")

def extract_info(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", html)
        email = emails[0] if emails else "Not found"

        insta = soup.find("a", href=re.compile("instagram.com"))
        fb = soup.find("a", href=re.compile("facebook.com"))

        return (
            email,
            insta["href"] if insta else "Not found",
            fb["href"] if fb else "Not found",
        )

    except:
        return "Error", "Error", "Error"

if extract_btn:
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
    urls = urls[:5]  # Free limit

    results = []
    for url in urls:
        email, ig, fb = extract_info(url)
        results.append({
            "Website": url,
            "Email": email,
            "Instagram": ig,
            "Facebook": fb,
        })

    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)
    st.download_button("Download CSV (5 rows)", csv, "results.csv", "text/csv")

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
