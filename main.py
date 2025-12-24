from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# ✅ VERY IMPORTANT: CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all websites (safe for now)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# Scraping Function
# ------------------------
def scrape_site(url: str):
    """
    Scrape emails from a given URL.
    Returns a list of emails found on the page.
    """
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        emails = set()
        for link in soup.find_all("a", href=True):
            if "mailto:" in link["href"]:
                emails.add(link["href"].replace("mailto:", ""))

        return list(emails)
    except Exception as e:
        # Return error info instead of breaking
        return {"error": str(e)}

# ------------------------
# Pydantic Model
# ------------------------
class ScrapeRequest(BaseModel):
    urls: List[str]

# ------------------------
# API Routes
# ------------------------
@app.get("/")
def root():
    return {"status": "API is running"}

@app.post("/scrape")
def scrape(request: ScrapeRequest):
    results = []
    for url in request.urls:
        results.append({url: scrape_site(url)})
    return {"results": results}
