
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from scraper import scrape_website

app = FastAPI(
    title="Website Email & Social Scraper API",
    description="Extract email and social media links from websites",
    version="1.0.0"
)

# -----------------------------
# REQUEST MODEL
# -----------------------------
class ScrapeRequest(BaseModel):
    websites: List[str]

# -----------------------------
# RESPONSE MODEL
# -----------------------------
class ScrapeResponse(BaseModel):
    results: List[dict]

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/")
def home():
    return {"status": "API is running"}

# -----------------------------
# SCRAPE ENDPOINT
# -----------------------------
@app.post("/scrape", response_model=ScrapeResponse)
def scrape_sites(data: ScrapeRequest):
    if not data.websites:
        raise HTTPException(status_code=400, detail="No websites provided")

    results = []
    for site in data.websites:
        results.append(scrape_website(site))

    return {"results": results}
