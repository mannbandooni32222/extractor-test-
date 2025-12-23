from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from scraper import scrape_website

app = FastAPI(
    title="Website Email & Social Scraper API",
    description="Extract emails and social links from websites",
    version="1.0.0"
)

# -------- REQUEST SCUND ----------
class ScrapeRequest(BaseModel):
    urls: List[str]

# -------- API ENDPOINT ----------
@app.post("/scrape")
def scrape_websites(data: ScrapeRequest):
    results = []

    for url in data.urls:
        results.append(scrape_website(url))

    return {
        "total_websites": len(results),
        "results": results
    }

# -------- HEALTH CHECK ----------
@app.get("/")
def health():
    return {"status": "API is running"}
