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
ADMIN_EMAILS = ["bandoonimann@gmail.com"]  # 🔴 CHANGE THIS

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
            return u
    return None

def register(email, password):
    data = load_users()

    for u in data["users"]:
        if u["email"] == email:
            return False

    role = "admin" if email in ADMIN_EMAILS else "user"

    data["users"].append({
        "email": email,
        "password": hash_password(password),
        "plan": "free",
        "role": role
    })

    save_users(data)
    return True

# ------------------------------
# SESSION INIT
# ------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------------------
# LOGIN / SIGNUP
# ------------------------------

if not st.session_state.logged_in:
    st.title("🔐 Login / Signup")

    choice = st.radio("Choose option", ["Login", "Signup"])

    if choice == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = authenticate(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_email = user["email"]
                st.session_state.user_role = user["role"]
                st.session_state.user_plan = user["plan"]
                st.rerun()
            else:
                st.error("Invalid email or password")

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

st.sidebar.success(f"Logged in as {st.session_state.user_email}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ------------------------------
# ADMIN DASHBOARD
# ------------------------------

def admin_dashboard():
    st.title("🛠 Admin Dashboard")

    data = load_users()
    users = data["users"]

    if not users:
        st.info("No users found")
        return

    df = pd.DataFrame(users)

    plan_filter = st.selectbox(
        "Filter by plan",
        ["All"] + sorted(df["plan"].unique())
    )

    if plan_filter != "All":
        df = df[df["plan"] == plan_filter]

    st.markdown("### 👥 Users")

    st.dataframe(
        df,
        use_container_width=True,
        height=600
    )

    csv = df.to_csv(index=False)
    st.download_button(
        "Download Users CSV",
        csv,
        "users.csv",
        "text/csv"
    )

# ------------------------------
# EXTRACTOR
# ------------------------------

def extractor():
    st.title("Free Email & Social Media Extractor")

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
        urls = urls[:10]  # FREE LIMIT

        results = []

        for url in urls:
            email, ig, fb = extract_info(url)
            results.append({
                "Website": url,
                "Email (1 only)": email,
                "Instagram": ig,
                "Facebook": fb
            })

        if len(urls_input.split("\n")) > 10:
            st.warning("Free plan allows only 10 websites.")

        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False)
        st.download_button(
            "Download CSV (10 rows)",
            csv,
            "results.csv",
            "text/csv"
        )

# ------------------------------
# ROUTING
# ------------------------------

if st.session_state.user_role == "admin":
    admin_dashboard()
else:
    extractor()

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
