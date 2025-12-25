from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import scrape_site
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://granthkosa.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    urls: List[str]

@app.get("/")
def root():
    return {"status": "API is running"}

@app.post("/scrape")
def scrape(request: ScrapeRequest):
    results = []
    for url in request.urls:
        results.append(scrape_site(url))
    return {"results": results}
