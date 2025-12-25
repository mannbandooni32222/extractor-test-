# scraper.py
import requests
from bs4 import BeautifulSoup
import re

def scrape_site(url):
    result = {
        "Website": url,
        "Email": "Not found",
        "Phone": "Not found",
        "Instagram": "Not found",
        "Facebook": "Not found",
        "LinkedIn": "Not found"
    }

    try:
        if not url.startswith("http"):
            url = "https://" + url

        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        html = res.text
        soup = BeautifulSoup(html, "html.parser")

        # Extract first email
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html)
        if emails:
            result["Email"] = emails[0]

        # Extract phone numbers
        phones = re.findall(r"\+?\d[\d\s\-]{7,}\d", html)
        if phones:
            result["Phone"] = phones[0]

        # Social links
        def find_social(domain):
            tag = soup.find("a", href=re.compile(domain))
            return tag["href"] if tag else "Not found"

        result["Instagram"] = find_social("instagram.com")
        result["Facebook"] = find_social("facebook.com")
        result["LinkedIn"] = find_social("linkedin.com")

    except Exception as e:
        print(f"Error scraping {url}: {e}")

    return result
