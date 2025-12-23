# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import scrape_site  # your scraper logic
from typing import List

app = FastAPI(title="Website Scraper API")

# -------------------------------
# CORS setup
# -------------------------------
origins = [
    "*"  # For testing, allows all domains. Replace with your domain in production e.g. "https://granthkosa.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://granthkosa.com"],  # replace with your WordPress URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Request/Response models
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
    results = []
    for url in request.urls:
        results.append(scrape_site(url))
    return {"results": results}
