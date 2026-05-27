from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from cachetools import TTLCache
import shutil
import os

from scraper import JobScraper
from cv_analyzer import CV_Analyzer

app = FastAPI(
    title="Intelligent Job Radar API",
    description="A API for agregaating job offers from different sources.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scraper = JobScraper()
cv_analyzer = CV_Analyzer()
search_cache = TTLCache(maxsize=100, ttl=300)

@app.post("/api/search")
async def search_and_match_jobs(
        category: str = Form(...),
        location: str = Form(...),
        experience: str = Form(...),
        cv_file: UploadFile = File(None)
):
    print(f"Searching for jobs {category}|{location}|{experience} ")

    cache_key = f"{category.lower().strip()}-{location.lower().strip()}-{experience.lower().strip()}"

    if cache_key in search_cache:
        print(f"Returning cached results")
        scraped_offers = search_cache[cache_key]
    else:
        print("Searching for offers")
        links = scraper.find_job_links(category, location, experience)
        if not links:
            raise HTTPException(status_code=404, detail="No offers found")

        scraped_offers = []
        for link in links:
            scraped_offers.append(scraper.extract_job_data(link))
        search_cache[cache_key] = scraped_offers

    cv_text =""
    if cv_file and cv_file.filename.endswith(".pdf"):
        print("CV file provided, analyzing...")
        temp_file_path = f"temp_{cv_file.filename}"

        try:
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(cv_file.file, buffer)

            cv_text = cv_analyzer.extract_text_from_pdf(temp_file_path)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                print("CV file removed")

    final_results = []
    for offer in scraped_offers:
        offer_data = offer.copy()

        if cv_text:
            score = cv_analyzer.calculate_match(cv_text, offer_data["tech_stack"])
            offer_data["match_score"] = score
        else:
            offer_data["match_score"] = 0.0

        final_results.append(offer_data)

    if cv_text:
        final_results.sort(key=lambda x: x["match_score"], reverse=True)
        print("Offers sorted by match score")


    return {
        "status": "success",
        "cv_analyzed": bool(cv_text),
        "total_analyzed": len(final_results),
        "data": final_results
    }