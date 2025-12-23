import requests
from bs4 import BeautifulSoup
import re

def scrape_website(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, timeout=10, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # -------- EMAIL (1 ONLY) ----------
        emails = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            html
        )
        email = emails[0] if emails else "Not found"

        # -------- SOCIAL LINKS ----------
        def find_social(domain):
            tag = soup.find("a", href=re.compile(domain))
            return tag["href"] if tag else "Not found"

        return {
            "website": url,
            "email": email,
            "instagram": find_social("instagram.com"),
            "facebook": find_social("facebook.com"),
            "linkedin": find_social("linkedin.com")
        }

    except Exception:
        return {
            "website": url,
            "email": "Error",
            "instagram": "Error",
            "facebook": "Error",
            "linkedin": "Error"
        }
