from scraper import JobScraper
from analyzer import JobAnalyzer

def run_radar(url:str):
    print("Starting the radar")

    scraper = JobScraper()
    analyzer = JobAnalyzer()

    print(f"\n[1/2] Scraping job data from {url}")
    job_data = scraper.extract_job_data(url)

    if job_data['full_description'] == "Error":
        print("Error scraping job data. Exiting.")
        return

    print(f"Downloaded successsfully. Found Tech Stack: {job_data['tech_stack']}")

    print(f"\n[2/2] Analyzing job data")
    text_to_analyze = f"{job_data['tech_stack']} {job_data['full_description']}"
    ai_results = analyzer.extract_key_info(text_to_analyze)

    #raport
    print("FINAL REPORT:")
    print(f"URL: {job_data['url']}")
    print(f"Language: {ai_results['language'].upper()}")
    print("-"*20)
    print(f"Experience: {ai_results['predicted_experience']} (Certainty: {ai_results['experience_confidence']}%)")
    print(f"Work mode: {ai_results['predicted_work_mode']} (Certainty: {ai_results['work_mode_confidence']}%)")

#test
if __name__ == "__main__":
    test_link = "https://justjoin.it/job-offer/fujitsu-poland-sp-z-o-o--junior-software-developer-with-c-c-linux-lodz-c"
    run_radar(test_link)