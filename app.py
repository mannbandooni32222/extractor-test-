

import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

st.title("Free Email & Social Media Extractor (MVP)")

# Input box
urls_input = st.text_area("Enter websites (one per line):")
extract_btn = st.button("Extract Information")

def extract_info(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        # Email extraction
        emails = list(set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", html)))
        email = emails[0] if emails else "Not found"

        # Instagram
        insta = soup.find("a", href=re.compile("instagram.com"))
        insta_link = insta["href"] if insta else "Not found"

        # Facebook
        fb = soup.find("a", href=re.compile("facebook.com"))
        fb_link = fb["href"] if fb else "Not found"

        return email, insta_link, fb_link

    except:
        return "Error", "Error", "Error"

if extract_btn:
    urls = urls_input.split("\n")
    urls = [u.strip() for u in urls if u.strip()]  # clean empty lines

    # LIMIT extraction to only 5 URLs
    limited_urls = urls[:5]

    results = []

    for url in limited_urls:
        email, ig, fb = extract_info(url)
        results.append({
            "Website": url,
            "Email": email,
            "Instagram": ig,
            "Facebook": fb
        })

    # Display message if user entered more than 5 URLs
    if len(urls) > 5:
        st.warning("Free version limit reached: Only 5 websites were extracted.")

    # Display results in table
    df = pd.DataFrame(results)
    st.subheader("Extracted Results (Max 5)")
    st.dataframe(df, use_container_width=True)

    # Download as CSV
    csv = df.to_csv(index=False)
    st.download_button("Download as CSV", csv, "results.csv", "text/csv")





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

