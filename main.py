from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import scrape_site
from typing import List

app = FastAPI(title="Website Scraper API")

# ✅ Add your WordPress domain here
origins = [
    "https://granthkosa.com",
    "http://localhost:3000",  # optional for local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # only allow your WordPress site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    urls: List[str]

@app.get("/")
def root():
    return {"status": "API is running"}

@app.post("/scrape")
def scrape_endpoint(request: ScrapeRequest):
    urls = request.urls
    plan = request.plan  # "free" or "paid"

    # Enforce limits
    if plan == "free":
        urls = urls[:10]  # limit free users

    results = []
    for url in urls:
        results.append(scrape_site(url))

    return {
        "plan": plan,
        "scraped": len(results),
        "results": results
    }
