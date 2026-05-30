import requests
from bs4 import BeautifulSoup
import json
from app.base_scraper import BaseScraper

class JjitScraper(BaseScraper):
    def __init__(self):
        super().__init__()

    def _find_offers_recursively(self, data, found_offers, seen_slugs):
        if isinstance(data, dict):
            if 'title' in data and 'slug' in data and 'companyName' in data:
                slug = data['slug']
                if slug not in seen_slugs:
                    seen_slugs.add(slug)
                    found_offers.append(data)
            else:
                for key, value in data.items():
                    self._find_offers_recursively(value, found_offers, seen_slugs)
        elif isinstance(data, list):
            for item in data:
                self._find_offers_recursively(item, found_offers, seen_slugs)
        pass

    def get_jobs(self, category: str, location: str, experience: str) -> list[dict]:
        url = f"https://justjoin.it/job-offers/{location.lower()}?experience-level={experience.lower()}&keyword={category}"
        print("Scanning JustJoin.it")

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            raw_offers = []
            seen_slugs = set()

            parts = response.text.split('self.__next_f.push(')

            for part in parts[1:]:
                end_idx = part.find('</script>')
                if end_idx != -1:
                    js_code = part[:end_idx].strip()

                    if js_code.endswith(');'):
                        js_code = js_code[:-2]
                    elif js_code.endswith(')'):
                        js_code = js_code[:-1]

                    try:
                        parsed_arr = json.loads(js_code)

                        if isinstance(parsed_arr, list) and len(parsed_arr) > 1:
                            payload = parsed_arr[1]

                            if isinstance(payload, str) and 'companyName' in payload and 'slug' in payload:

                                colon_idx = payload.find(':')
                                if colon_idx != -1:
                                    clean_json_str = payload[colon_idx + 1:]

                                    inner_data = json.loads(clean_json_str)

                                    #print("encoded")
                                    self._find_offers_recursively(inner_data, raw_offers, seen_slugs)
                    except Exception:
                        continue

            if not raw_offers:
                print("Could not find any offers on JustJoin.it.")
                return []

            print(f"Found {len(raw_offers)} raw offers")

            standardized_offers = []
            for offer in raw_offers:
                tech_stack_list = []
                skills = offer.get("requiredSkills") or offer.get("skills") or []
                for skill in skills:
                    if isinstance(skill, dict) and 'name' in skill:
                        tech_stack_list.append(skill['name'])
                    elif isinstance(skill, str):
                        tech_stack_list.append(skill)

                tech_stack = ", ".join(tech_stack_list) if tech_stack_list else "Not found"
                offer_url = f"https://justjoin.it/offers/{offer.get('slug')}"

                standardized_offers.append({
                    "url": offer_url,
                    "title": offer.get("title", "Brak tytułu"),
                    "company": offer.get("companyName", "Brak firmy"),
                    "tech_stack": tech_stack
                })

            return standardized_offers

        except Exception as e:
            print(f"Error during downloading data {e}")
            return []

    def extract_job_data(self, url: str):
        pass