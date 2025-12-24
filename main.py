from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from scraper import scrape_site

app = FastAPI()

# -------------------------------
# CORS FIX (THIS IS IMPORTANT)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # your WordPress site
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
    results = []
    for url in request.urls:
        results.append(scrape_site(url))
    return {"results": results}
