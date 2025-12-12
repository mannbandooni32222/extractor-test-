import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Free Email & Social Media Extractor", layout="wide")
st.title("Free Email & Social Media Extractor (MVP)")

st.write("""
Enter website URLs (one per line) to extract up to **5 emails**, Facebook, and Instagram links.
""")

urls_input = st.text_area("Website URLs", placeholder="https://example.com\nhttps://another.com")
urls = [url.strip() for url in urls_input.splitlines() if url.strip()]

if st.button("Extract"):
    if not urls:
        st.warning("Please enter at least one URL.")
    else:
        results = {}
        for url in urls:
            try:
                r = requests.get(url, timeout=5)
                soup = BeautifulSoup(r.text, 'html.parser')
                html_text = soup.get_text()

                # Extract emails (limit 5)
                emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html_text)
                emails = emails[:5]

                # Extract social media links
                links = [a['href'] for a in soup.find_all('a', href=True)]
                fb = [link for link in links if "facebook.com" in link]
                insta = [link for link in links if "instagram.com" in link]

                results[url] = {
                    "Emails": emails,
                    "Facebook": fb,
                    "Instagram": insta
                }
            except Exception as e:
                results[url] = {"Error": str(e)}

        # Display results
        for site, data in results.items():
            st.subheader(site)
            if "Error" in data:
                st.error(data["Error"])
            else:
                st.write("Emails:", data["Emails"])
                st.write("Facebook:", data["Facebook"])
                st.write("Instagram:", data["Instagram"])




import streamlit as st

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
    results = []

    for url in urls:
        email, ig, fb = extract_info(url)
        results.append({
            "Website": url.strip(),
            "Email": email,
            "Instagram": ig,
            "Facebook": fb
        })

    # Display results in table
    df = pd.DataFrame(results)
    st.subheader("Extracted Results")
    st.dataframe(df, use_container_width=True)

    # Allow download as CSV
    csv = df.to_csv(index=False)
    st.download_button("Download as CSV", csv, "results.csv", "text/csv")

