from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import JobScraper
from cachetools import TTLCache

app = FastAPI(
    title="Intelligent Job Radar API",
    description="A API for agregaating job offers from different sources.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scraper = JobScraper()

search_cache = TTLCache(maxsize=100, ttl=300)

class JobSearchRequest(BaseModel):
    category: str
    location: str
    experience: str

@app.post("/api/search")
async def search_job_offers(request: JobSearchRequest):
    cache_key = f"{request.category.lower()}-{request.location.lower()}-{request.experience.lower()}"
    if cache_key in search_cache:
        print(f"Returning cached results: {cache_key}")
        return search_cache[cache_key]

    print(f"No cache hit. Scraping the web for job offers: {cache_key}")

    links = scraper.find_job_links(request.category, request.location, request.experience)

    if not links:
        raise HTTPException(
            status_code=404,
            detail="No job offers found.")

    top_results = []
    for link in links[:5]:
        data = scraper.extract_job_data(link)
        top_results.append(data)

    response_data = {
        "status":"Success",
        "total_offers_found":len(links),
        "top_offers_analyzed":len(top_results),
        "data": top_results
    }

    search_cache[cache_key] = response_data
    return response_data