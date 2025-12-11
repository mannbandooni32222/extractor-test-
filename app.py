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
