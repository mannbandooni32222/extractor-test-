import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Website Email & Social Scraper",
    layout="wide"
)

st.title("Website Email & Social Media Scraper")
st.write("Extract emails and social links from public websites.")

# -----------------------------
# PLAN LOGIC (FROM WORDPRESS)
# -----------------------------
query_params = st.query_params
plan = query_params.get("plan", ["free"])[0]

FREE_LIMIT = 10
is_paid = plan == "paid"

if is_paid:
    st.success("✅ Paid Plan: Unlimited scraping enabled")
else:
    st.info("🆓 Free Plan: Limited to 10 websites")

# -----------------------------
# INPUT
# -----------------------------
urls_input = st.text_area(
    "Enter website URLs (one per line)",
    height=200,
    placeholder="example.com\nhttps://example.org"
)

start_btn = st.button("🚀 Start Scraping")

# -----------------------------
# SCRAPER FUNCTION
# -----------------------------
def scrape_website(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=10, headers=headers)
        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        # Extract first email only
        emails = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            html
        )
        email = emails[0] if emails else "Not found"

        def find_social(domain):
            tag = soup.find("a", href=re.compile(domain))
            return tag["href"] if tag else "Not found"

        return {
            "Website": url,
            "Email": email,
            "Instagram": find_social("instagram.com"),
            "Facebook": find_social("facebook.com"),
            "LinkedIn": find_social("linkedin.com")
        }

    except Exception:
        return {
            "Website": url,
            "Email": "Error",
            "Instagram": "Error",
            "Facebook": "Error",
            "LinkedIn": "Error"
        }

# -----------------------------
# RUN SCRAPER
# -----------------------------
if start_btn:
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    if not urls:
        st.error("Please enter at least one website.")
        st.stop()

    # Apply free plan limit
    if not is_paid:
        urls = urls[:FREE_LIMIT]

    results = []

    with st.spinner("Scraping websites..."):
        for url in urls:
            results.append(scrape_website(url))

    df = pd.DataFrame(results)

    st.success(f"Scraped {len(df)} websites")
    st.dataframe(df, use_container_width=True, height=500)

    csv = df.to_csv(index=False)
    st.download_button(
        "⬇ Download CSV",
        csv,
        "scraped_results.csv",
        "text/csv"
    )

    if not is_paid:
        st.warning("Free plan limit reached. Upgrade to unlock unlimited scraping.")

# -----------------------------
# CLEAN UI
# -----------------------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
