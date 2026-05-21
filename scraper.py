import requests
from bs4 import BeautifulSoup
import time

class JobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def extract_job_data(self, url: str) -> dict:
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            tech_section = soup.find('ul', class_='mui-vdxqko')
            tech_stack = tech_section.get_text(separator=',',strip=True) if tech_section else "Not found"

            description_section = soup.find('div', class_='MuiBox-root mui-n1fnon')
            description = description_section.get_text(separator=' ', strip=True) if description_section else "Not found"

            return{
                "url":url,
                "tech_stack":tech_stack,
                "full_description":description
            }

        except Exception as e:
            print(f"Error fetching job data {url}: {e}")
            return {"url": url, "tech_stack": "Error", "full_description": "Error"}


#test
if __name__ == "__main__":
    scraper = JobScraper()

    test_url = "https://justjoin.it/job-offer/fujitsu-poland-sp-z-o-o--junior-software-developer-with-c-c-linux-lodz-c"

    data = scraper.extract_job_data(test_url)
    print("\n================ RESULTS ================")
    print(f"LINK: {data['url']}\n")
    print(f"TECH STACK:\n{data['tech_stack']}\n")
    print("--------------------------------------------------")
    print(f"DESCRIPTION (FIRST 300 SIGNS):\n{data['full_description'][:300]}...")
    print("==================================================")