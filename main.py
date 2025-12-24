# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import scrape_site
from typing import List

app = FastAPI(title="Website Scraper API")

# -------------------------------
# CORS setup (allow WordPress site)
# -------------------------------
origins = [
    "https://your-wordpress-site.com"  # Replace with your WordPress domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Request model
# -------------------------------
class ScrapeRequest(BaseModel):
    urls: List[str]

# -------------------------------
# Routes
# -------------------------------
@app.get("/")
def root():
    return {"status": "API is running"}

@app.post("/scrape")
def scrape_endpoint(request: ScrapeRequest):
    results = [scrape_site(url) for url in request.urls]
    return {"results": results}
