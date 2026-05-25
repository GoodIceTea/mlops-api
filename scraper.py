import requests
from bs4 import BeautifulSoup
from typing import List
import json

class JobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.base_url = "https://justjoin.it"

    def find_job_links(self, category: str, location: str, experience: str) -> list[str]:
        search_url=f"{self.base_url}/{location.lower()}?experience-level={experience.lower()}&keyword={category.lower()}"
        print("Searching for jobs...")
        #print(f"URL: {search_url}")

        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            offer_links = []
            scripts = soup.find_all('script', type='application/ld+json')

            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get("@type") == "CollectionPage" and "hasPart" in data:
                        for item in data["hasPart"]:
                            if "url" in item:
                                offer_links.append(item["url"])
                except json.JSONDecodeError:
                    continue

            return offer_links

        except Exception as e:
            print(f"Error finding job offers: {e}")
            return []

    def extract_job_data(self, url: str) -> dict:
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            tech_section = soup.find('ul', class_='mui-vdxqko')
            tech_stack = tech_section.get_text(separator=',',strip=True) if tech_section else "Not found"

            return{
                "url":url,
                "tech_stack":tech_stack,
            }

        except Exception as e:
            print(f"Error fetching job data {url}: {e}")
            return {"url": url, "tech_stack": "Error"}


#test
if __name__ == "__main__":
    scraper = JobScraper()

    print("Starting the scraper...")
    found_links = scraper.find_job_links(category="data", location="lodz", experience="junior")

    print(f"\nFound {len(found_links)} offers!")

    for i, link in enumerate(found_links[:3]):#pierwsze 3
        print(f"\n--- Offer {i + 1} ---")
        dane = scraper.extract_job_data(link)
        print(f"Link:  {dane['url']}")
        print(f"Stack: {dane['tech_stack']}")