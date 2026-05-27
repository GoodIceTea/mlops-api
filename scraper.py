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

            job_title = "No title"
            company_name = "No company"

            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get("@type") == "JobPosting":
                        job_title = data.get("title", "No title")
                        org = data.get("hiringOrganization", {})
                        company_name = org.get("name", "No company")
                        break
                except (json.JSONDecodeError, TypeError):
                    continue

            if job_title == "No title":
                h1_tag = soup.find('h1')
                job_title = h1_tag.get_text(strip=True) if h1_tag else "No title"

            tech_section = soup.find('ul', class_='mui-vdxqko')
            if tech_section:
                raw_text = tech_section.get_text(separator=',', strip=True)
                raw_list = [item.strip() for item in raw_text.split(',')]
                tech_stack = ', '.join(raw_list[::2])
            else:
                tech_stack = "Not found"

            return{
                "url":url,
                "title": job_title,
                "company": company_name,
                "tech_stack":tech_stack
            }

        except Exception as e:
            print(f"Error fetching job data {url}: {e}")
            return {"url": url, "tech_stack": "Error"}