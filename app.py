import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(layout="wide")

# --------------------------------------------------
# CUSTOM MINIMAL CSS (BRAND COLORS)
# --------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: Inter, system-ui, sans-serif;
    background-color: #ffffff;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
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

/* Table */
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

        # Email (first found)
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
            "LinkedIn": social("linkedin.com"),
        }

    except:
        return {
            "Website": url,
            "Email": "Error",
            "Instagram": "Error",
            "Facebook": "Error",
            "LinkedIn": "Error",
        }

# --------------------------------------------------
# RUN SCRAPER
# --------------------------------------------------
if start:
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    if not urls:
        st.stop()

    results = []

    with st.spinner("Scraping..."):
        for url in urls:
            results.append(scrape_site(url))

    df = pd.DataFrame(results)

    st.dataframe(df, use_container_width=True, height=520)

    csv = df.to_csv(index=False)
    st.download_button(
        "Download CSV",
        csv,
        "scraped_results.csv",
        "text/csv"
    )
