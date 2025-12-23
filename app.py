import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Website Email & Social Scraper",
    layout="wide"
)

# 🔧 MANUAL PLAN CONTROL (ADMIN)
# Change this to True to unlock paid features
PAID_USER = False   # <-- ADMIN TOGGLE
FREE_LIMIT = 10

# --------------------------------------------------
# CUSTOM CSS (BRAND UI)
# --------------------------------------------------
st.markdown("""
<style>
/* Global */
html, body, [class*="css"] {
    font-family: Inter, system-ui, sans-serif;
    background-color: #ffffff;
}

/* Center container */
.block-container {
    max-width: 1100px;
    padding-top: 3rem;
}

/* Header */
.app-title {
    font-size: 36px;
    font-weight: 600;
    color: #111;
}

.app-subtitle {
    font-size: 16px;
    color: #555;
    margin-bottom: 1.5rem;
}

/* Plan badge */
.plan-badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 14px;
    margin-bottom: 2rem;
}

.plan-free {
    background-color: rgba(76,0,177,0.08);
    color: #4c00b1;
}

.plan-paid {
    background-color: #4c00b1;
    color: #ffffff;
}

/* Textarea */
textarea {
    border-radius: 10px !important;
    border: 1px solid #ddd !important;
}

/* Primary button */
.stButton > button {
    background-color: #4c00b1;
    color: #ffffff;
    border-radius: 10px;
    padding: 10px 22px;
    border: none;
    font-weight: 500;
}

.stButton > button:hover {
    background-color: #3b008f;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    border: 1px solid #eee;
}

/* Download button */
.stDownloadButton > button {
    background-color: #ffffff;
    color: #4c00b1;
    border: 1px solid #4c00b1;
    border-radius: 10px;
    padding: 8px 18px;
}

.stDownloadButton > button:hover {
    background-color: rgba(76,0,177,0.05);
}

/* Hide Streamlit UI */
#MainMenu, footer, header {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown('<div class="app-title">Website Email & Social Scraper</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Extract emails and social links from public websites</div>', unsafe_allow_html=True)

# Plan Badge
if PAID_USER:
    st.markdown('<div class="plan-badge plan-paid">✅ Paid Plan – Unlimited scraping</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="plan-badge plan-free">🆓 Free Plan – 10 websites</div>', unsafe_allow_html=True)

# --------------------------------------------------
# INPUT
# --------------------------------------------------
urls_input = st.text_area(
    "Enter website URLs (one per line)",
    height=200,
    placeholder="example.com\nhttps://example.org"
)

start = st.button("Start Scraping")

# --------------------------------------------------
# SCRAPER FUNCTION
# --------------------------------------------------
def scrape_site(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, timeout=12, headers=headers)
        html = res.text
        soup = BeautifulSoup(html, "html.parser")

        # Email (1 only)
        emails = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            html
        )
        email = emails[0] if emails else "Not found"

        def social(domain):
            tag = soup.find("a", href=re.compile(domain))
            return tag["href"] if tag else "Not found"

        return {
            "Website": url,
            "Email": email,
            "Instagram": social("instagram.com"),
            "Facebook": social("facebook.com"),
            "LinkedIn": social("linkedin.com")
        }

    except:
        return {
            "Website": url,
            "Email": "Error",
            "Instagram": "Error",
            "Facebook": "Error",
            "LinkedIn": "Error"
        }

# --------------------------------------------------
# RUN SCRAPER
# --------------------------------------------------
if start:
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    if not urls:
        st.error("Please enter at least one website.")
        st.stop()

    if not PAID_USER:
        urls = urls[:FREE_LIMIT]

    results = []

    with st.spinner("Scraping websites..."):
        for url in urls:
            results.append(scrape_site(url))

    df = pd.DataFrame(results)

    st.success(f"Scraped {len(df)} websites")
    st.dataframe(df, use_container_width=True, height=520)

    csv = df.to_csv(index=False)
    st.download_button(
        "Download CSV",
        csv,
        "scraped_results.csv",
        "text/csv"
    )

    if not PAID_USER and len(urls_input.split("\n")) > FREE_LIMIT:
        st.warning("Free plan limit reached. Upgrade to unlock unlimited scraping.")
