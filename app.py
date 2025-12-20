import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import firebase_admin
from firebase_admin import credentials, auth, firestore

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Website Scraper SaaS", layout="wide")

# -----------------------------
# FIREBASE INIT
# -----------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": st.secrets["FIREBASE_PROJECT_ID"],
        "client_email": st.secrets["FIREBASE_CLIENT_EMAIL"],
        "private_key": st.secrets["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
        "token_uri": "https://oauth2.googleapis.com/token",
    })
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -----------------------------
# SESSION STATE
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -----------------------------
# AUTH FUNCTIONS
# -----------------------------
def signup(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({
            "email": email,
            "plan": "free",
            "usage": 0,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception as e:
        st.error(e)
        return False


def login(email):
    users = db.collection("users").where("email", "==", email).limit(1).stream()
    for u in users:
        return u.id, u.to_dict()
    return None, None


# -----------------------------
# LOGIN / SIGNUP UI
# -----------------------------
if not st.session_state.logged_in:
    st.title("🔐 Login / Signup")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        email = st.text_input("Email")
        if st.button("Login"):
            uid, user = login(email)
            if user:
                st.session_state.logged_in = True
                st.session_state.uid = uid
                st.session_state.plan = user["plan"]
                st.session_state.usage = user["usage"]
                st.rerun()
            else:
                st.error("User not found")

    with tab2:
        email = st.text_input("Signup Email")
        password = st.text_input("Password", type="password")
        if st.button("Create Account"):
            if signup(email, password):
                st.success("Account created. Please login.")

    st.stop()

# -----------------------------
# LOGOUT
# -----------------------------
st.sidebar.success(f"Logged in ({st.session_state.plan})")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# -----------------------------
# SCRAPER FUNCTION
# -----------------------------
def scrape_site(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        html = res.text
        soup = BeautifulSoup(html, "html.parser")

        email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html)
        email = email[0] if email else "Not found"

        def find_social(domain):
            tag = soup.find("a", href=re.compile(domain))
            return tag["href"] if tag else "Not found"

        return {
            "Website": url,
            "Email": email,
            "Instagram": find_social("instagram.com"),
            "Facebook": find_social("facebook.com"),
            "LinkedIn": find_social("linkedin.com"),
        }
    except:
        return {
            "Website": url,
            "Email": "Error",
            "Instagram": "Error",
            "Facebook": "Error",
            "LinkedIn": "Error",
        }

# -----------------------------
# APP UI
# -----------------------------
st.title("🌐 Website Email & Social Scraper")

FREE_LIMIT = 10
urls_input = st.text_area("Enter websites (one per line)", height=200)
run = st.button("🚀 Start Scraping")

if run:
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    if st.session_state.plan == "free":
        remaining = FREE_LIMIT - st.session_state.usage
        urls = urls[:remaining]

    results = []
    for url in urls:
        results.append(scrape_site(url))

    # Update usage
    db.collection("users").document(st.session_state.uid).update({
        "usage": firestore.Increment(len(results))
    })

    st.session_state.usage += len(results)

    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True, height=600)

    csv = df.to_csv(index=False)
    st.download_button("⬇ Download CSV", csv, "results.csv", "text/csv")

    if st.session_state.plan == "free" and st.session_state.usage >= FREE_LIMIT:
        st.warning("Free limit reached. Upgrade to continue.")

# -----------------------------
# HIDE STREAMLIT UI
# -----------------------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
