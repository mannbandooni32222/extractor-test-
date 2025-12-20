import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json
from pathlib import Path

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="Website Scraper SaaS", layout="wide")
USER_DB = Path("users.json")
ADMIN_EMAILS = ["admin@example.com"]  # Change this to your admin email
FREE_LIMIT = 10

# ----------------------------
# HELPERS
# ----------------------------
def load_users():
    if USER_DB.exists():
        with open(USER_DB, "r") as f:
            return json.load(f)
    return {"users": []}

def save_users(data):
    with open(USER_DB, "w") as f:
        json.dump(data, f, indent=4)

def register(email):
    data = load_users()
    for u in data["users"]:
        if u["email"] == email:
            return False
    role = "admin" if email in ADMIN_EMAILS else "user"
    plan = "free"
    data["users"].append({
        "email": email,
        "role": role,
        "plan": plan,
        "usage": 0
    })
    save_users(data)
    return True

def get_user(email):
    users = load_users()["users"]
    for u in users:
        if u["email"] == email:
            return u
    return None

def update_user(email, key, value):
    data = load_users()
    for u in data["users"]:
        if u["email"] == email:
            u[key] = value
    save_users(data)

# ----------------------------
# SESSION STATE
# ----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ----------------------------
# LOGIN / SIGNUP UI
# ----------------------------
if not st.session_state.logged_in:
    st.title("🔐 Login / Signup")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        login_email = st.text_input("Email")
        if st.button("Login"):
            user = get_user(login_email)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_email = login_email
                st.session_state.user_role = user["role"]
                st.session_state.user_plan = user["plan"]
                st.session_state.user_usage = user["usage"]
                st.success(f"Logged in as {login_email}")
                st.experimental_rerun()
            else:
                st.error("User not found. Please signup.")

    with tab2:
        signup_email = st.text_input("Signup Email")
        if st.button("Create Account"):
            if register(signup_email):
                st.success("Account created! Please login.")
            else:
                st.error("Email already exists.")
    st.stop()

# ----------------------------
# LOGOUT
# ----------------------------
st.sidebar.success(f"Logged in ({st.session_state.user_plan})")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.experimental_rerun()

# ----------------------------
# ADMIN DASHBOARD
# ----------------------------
def admin_dashboard():
    st.title("🛠 Admin Dashboard")
    data = load_users()
    users = data["users"]
    if not users:
        st.info("No users found.")
        return

    df = pd.DataFrame(users)
    plan_filter = st.selectbox("Filter by plan", ["All"] + sorted(df["plan"].unique()))
    if plan_filter != "All":
        df = df[df["plan"] == plan_filter]

    st.markdown("### 👥 Users")
    st.dataframe(df, use_container_width=True, height=600)

    # Upgrade / Downgrade users
    st.markdown("### ⚙ Change User Plan")
    email_to_change = st.text_input("Enter user email")
    new_plan = st.selectbox("Select new plan", ["free", "paid"])
    if st.button("Update Plan"):
        if get_user(email_to_change):
            update_user(email_to_change, "plan", new_plan)
            st.success(f"Updated {email_to_change} to {new_plan} plan")
        else:
            st.error("User not found.")

    csv = df.to_csv(index=False)
    st.download_button("Download Users CSV", csv, "users.csv", "text/csv")

# ----------------------------
# SCRAPER FUNCTION
# ----------------------------
def scrape_website(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        html = res.text
        soup = BeautifulSoup(html, "html.parser")

        email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html)
        email = email[0] if email else "Not found"

        def social_link(domain):
            tag = soup.find("a", href=re.compile(domain))
            return tag["href"] if tag else "Not found"

        return {
            "Website": url,
            "Email": email,
            "Instagram": social_link("instagram.com"),
            "Facebook": social_link("facebook.com"),
            "LinkedIn": social_link("linkedin.com")
        }
    except:
        return {"Website": url, "Email": "Error", "Instagram": "Error", "Facebook": "Error", "LinkedIn": "Error"}

# ----------------------------
# SCRAPER UI
# ----------------------------
def scraper_ui():
    st.title("🌐 Website Email & Social Media Scraper")

    uploaded_file = st.file_uploader("Upload CSV with websites (optional)")
    urls_input = st.text_area("Or enter websites (one per line)")

    run_btn = st.button("🚀 Start Scraping")
    urls = []

    if uploaded_file:
        try:
            df_input = pd.read_csv(uploaded_file)
            if 'website' in df_input.columns:
                urls += df_input['website'].dropna().tolist()
            else:
                st.warning("CSV must have 'website' column")
        except Exception as e:
            st.error(f"CSV Error: {e}")

    if urls_input:
        urls += [u.strip() for u in urls_input.split("\n") if u.strip()]

    if run_btn:
        if st.session_state.user_plan == "free":
            remaining = FREE_LIMIT - st.session_state.user_usage
            urls = urls[:remaining]
            if st.session_state.user_usage + len(urls) >= FREE_LIMIT:
                st.warning("Free limit reached. Upgrade to paid for unlimited scraping.")

        results = []
        for url in urls:
            results.append(scrape_website(url))

        # Update usage
        if st.session_state.user_plan == "free":
            st.session_state.user_usage += len(results)
            update_user(st.session_state.user_email, "usage", st.session_state.user_usage)

        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, height=600)

        csv = df.to_csv(index=False)
        st.download_button("⬇ Download CSV", csv, "scraped_results.csv", "text/csv")

# ----------------------------
# PLACEHOLDER RAZORPAY
# ----------------------------
def razorpay_placeholder():
    st.info("💳 Upgrade to paid is not live yet. You can manually change plan in admin dashboard.")

# ----------------------------
# ROUTING
# ----------------------------
if st.session_state.user_role == "admin":
    admin_dashboard()
else:
    scraper_ui()
    razorpay_placeholder()

# ----------------------------
# HIDE STREAMLIT UI
# ----------------------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
