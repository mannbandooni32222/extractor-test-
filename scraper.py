# scraper.py
import requests
from bs4 import BeautifulSoup
import re

def scrape_site(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        html = res.text
        soup = BeautifulSoup(html, "html.parser")

        # Extract first email
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html)
        email = emails[0] if emails else "Not found"

        # Social links
        def find_social(domain):
            tag = soup.find("a", href=re.compile(domain))
            return tag["href"] if tag else "Not found"

        return {
            "Website": url,
            "Email": email,
            "Instagram": find_social("instagram.com"),
            "Facebook": find_social("facebook.com"),
            "LinkedIn": find_social("linkedin.com"),
        }
    except Exception as e:
        return {
            "Website": url,
            "Email": "Error",
            "Instagram": "Error",
            "Facebook": "Error",
            "LinkedIn": "Error",
        }
