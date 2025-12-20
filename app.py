import firebase_admin
from firebase_admin import credentials, auth, firestore
import streamlit as st

if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": st.secrets["FIREBASE_PROJECT_ID"],
        "client_email": st.secrets["FIREBASE_CLIENT_EMAIL"],
        "private_key": st.secrets["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
        "token_uri": "https://oauth2.googleapis.com/token"
    })
    firebase_admin.initialize_app(cred)

db = firestore.client()

def signup_user(email, password):
    try:
        user = auth.create_user(
            email=email,
            password=password
        )

        # Create Firestore user document
        db.collection("users").document(user.uid).set({
            "email": email,
            "plan": "free",
            "role": "user",
            "usage_count": 0,
            "created_at": firestore.SERVER_TIMESTAMP,
            "paid_at": None
        })

        return True
    except Exception as e:
        st.error(str(e))
        return False
def get_user_by_email(email):
    users = db.collection("users").where("email", "==", email).limit(1).stream()
    for u in users:
        return u.id, u.to_dict()
    return None, None

uid, user_data = get_user_by_email(email)

st.session_state.uid = uid
st.session_state.plan = user_data["plan"]
st.session_state.usage = user_data["usage_count"]

def increase_usage(uid, count):
    user_ref = db.collection("users").document(uid)
    user_ref.update({
        "usage_count": firestore.Increment(count)
    })


import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Website Scraper",
    layout="wide"
)

st.title("🌐 Website Email & Social Media Scraper")
st.write("Extract emails and social links from public websites.")

# ----------------------------
# PLAN SELECTION (MVP LOGIC)
# ----------------------------
st.sidebar.title("💼 Your Plan")

plan = st.sidebar.radio(
    "Choose plan",
    ["Free", "Paid ($5/month)"]
)

FREE_LIMIT = 10

if plan == "Free":
    st.sidebar.info("Free plan: 10 websites per run")
else:
    st.sidebar.success("Paid plan: Unlimited scraping")

# ----------------------------
# INPUT
# ----------------------------
urls_input = st.text_area(
    "Enter website URLs (one per line)",
    height=200,
    placeholder="example.com\nhttps://example.org"
)

extract_btn = st.button("🚀 Start Scraping")

# ----------------------------
# SCRAPER FUNCTION
# ----------------------------
def scrape_website(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=10, headers=headers)
        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        # 1 Email only
        emails = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            html
        )
        email = emails[0] if emails else "Not found"

        # Social links
        insta = soup.find("a", href=re.compile("instagram.com"))
        fb = soup.find("a", href=re.compile("facebook.com"))
        linkedin = soup.find("a", href=re.compile("linkedin.com"))

        return {
            "Website": url,
            "Email": email,
            "Instagram": insta["href"] if insta else "Not found",
            "Facebook": fb["href"] if fb else "Not found",
            "LinkedIn": linkedin["href"] if linkedin else "Not found"
        }

    except:
        return {
            "Website": url,
            "Email": "Error",
            "Instagram": "Error",
            "Facebook": "Error",
            "LinkedIn": "Error"
        }

# ----------------------------
# RUN SCRAPER
# ----------------------------
if extract_btn:
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    if not urls:
        st.error("Please enter at least one website.")
        st.stop()

    # FREE PLAN LIMIT
    if plan == "Free" and len(urls) > FREE_LIMIT:
        st.warning(f"Free plan allows only {FREE_LIMIT} websites.")
        urls = urls[:FREE_LIMIT]

    results = []

    with st.spinner("Scraping websites..."):
        for url in urls:
            results.append(scrape_website(url))

    df = pd.DataFrame(results)

    st.success(f"Scraped {len(df)} websites")
    st.dataframe(df, use_container_width=True, height=600)

    # CSV DOWNLOAD LIMIT
    if plan == "Free":
        df_download = df.head(FREE_LIMIT)
        st.info("Free plan CSV limited to 10 rows.")
    else:
        df_download = df

    csv = df_download.to_csv(index=False)
    st.download_button(
        "⬇ Download CSV",
        csv,
        "scraped_results.csv",
        "text/csv"
    )

    # UPGRADE CTA
    if plan == "Free":
        st.markdown(
            "💡 **Upgrade to Paid ($5/month) for unlimited scraping**",
            unsafe_allow_html=True
        )

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
