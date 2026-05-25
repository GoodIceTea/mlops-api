from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scraper import JobScraper
app = FastAPI(
    title="Intelligent Job Radar API",
    description="A API for agregaating job offers from different sources.",
    version="2.0.0",
)

scraper = JobScraper()

class JobSearchRequest(BaseModel):
    category: str
    location: str
    experience: str

@app.post("/api/search")
async def search_job_offers(request: JobSearchRequest):
    print(f"Recieved request: {request.category} in {request.location} with experience {request.experience}")

    links = scraper.find_job_links(request.category, request.location, request.experience)

    if not links:
        raise HTTPException(
            status_code=404,
            detail="No job offers found.")

    top_results = []
    for link in links[:3]:
        data = scraper.extract_job_data(link)
        top_results.append(data)

    return {
        "status":"Success",
        "total_offers_found":len(links),
        "top_offers_analyzed":len(top_results),
        "data": top_results
    }