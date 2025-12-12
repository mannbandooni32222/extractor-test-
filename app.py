
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

