# scraper.py
import requests
from bs4 import BeautifulSoup
import re

def scrape_site(url):
    try:
        # Ensure URL starts with http/https
        if not url.startswith("http"):
            url = "https://" + url

        # Get HTML content
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        html = res.text
        soup = BeautifulSoup(html, "html.parser")

        # --- Extract Emails ---
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html)
        email = emails[0] if emails else "N/A"

        # --- Extract Phone Numbers ---
        phones = re.findall(r"\+?\d[\d\s\-\(\)]{7,}\d", html)
        phone = phones[0] if phones else "N/A"

        # --- Extract Social Links ---
        def find_social(domain):
            links = soup.find_all("a", href=re.compile(domain, re.I))
            return links[0]["href"] if links else "N/A"

        instagram = find_social("instagram.com")
        facebook = find_social("facebook.com")
        linkedin = find_social("linkedin.com")

        return {
            "Website": url,
            "Email": email,
            "Phone": phone,
            "Instagram": instagram,
            "Facebook": facebook,
            "LinkedIn": linkedin,
        }

    except Exception as e:
        # Return error if something goes wrong
        return {
            "Website": url,
            "Email": "Error",
            "Phone": "Error",
            "Instagram": "Error",
            "Facebook": "Error",
            "LinkedIn": "Error",
        }
