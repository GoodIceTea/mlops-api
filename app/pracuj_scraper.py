import requests
from bs4 import BeautifulSoup
import json

class PracujScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7'
        }

    def _find_offers_recursively(self, data, found_offers):
        if isinstance(data, dict):
            if 'jobTitle' in data and 'companyName' in data:
                found_offers.append(data)
            else:
                for key, value in data.items():
                    self._find_offers_recursively(value, found_offers)
        elif isinstance(data, list):
            for item in data:
                self._find_offers_recursively(item, found_offers)

    def get_jobs(self, category: str, location: str, experience: str) -> list[dict]:
        exp_map = {
            "junior": "17",
            "mid": "4",
            "senior": "18"
        }
        exp_code = exp_map.get(experience.lower(), "17")
        url = f"https://it.pracuj.pl/praca/{category.lower()};kw/{location.lower()};wp?rd=30&et={exp_code}"
        return self.extract_jobs_from_url(url)

    def extract_jobs_from_url(self, url: str) -> list[dict]:
        print(f"Scanning Pracuj.pl: {url}")
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            next_data_script = soup.find('script', id='__NEXT_DATA__')

            if not next_data_script:
                print("Tag __NEXT_DATA__ not found")
                return []

            raw_json = json.loads(next_data_script.string)
            raw_offers = []
            self._find_offers_recursively(raw_json, raw_offers)

            print(f"Found {len(raw_offers)} raw offers")

            standardized_offers = []
            for offer in raw_offers:
                tech_list = offer.get("technologies", [])
                tech_stack = ", ".join(tech_list) if tech_list else "Not found"

                offer_url = url
                if "offers" in offer and isinstance(offer["offers"], list) and len(offer["offers"]) > 0:
                    offer_url = offer["offers"][0].get("offerAbsoluteUri", url)
                elif "offerAbsoluteUri" in offer:
                    offer_url = offer["offerAbsoluteUri"]

                standardized_offers.append({
                    "url": offer_url,
                    "title": offer.get("jobTitle", "No title"),
                    "company": offer.get("companyName", "No company"),
                    "tech_stack": tech_stack
                })

            return standardized_offers

        except Exception as e:
            print(f"Error during downloading data: {e}")
            return []

if __name__ == "__main__":
    scraper = PracujScraper()
    test_url = "https://it.pracuj.pl/praca/python;kw/lodz;wp?rd=30&et=17"
    results = scraper.extract_jobs_from_url(test_url)
    print("\n3 top results")
    for i, offer in enumerate(results[:3]):
        print(f"[{i+1}] {offer['title']} - {offer['company']}")
        print(f"Tech stack: {offer['tech_stack']}")
        print(f"URL: {offer['url']}\n")

