import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from scraper.base_scraper import BaseScraper

class GenericBoardScraper(BaseScraper):
    def __init__(self):
        super().__init__("GenericPortal")

    def scrape(self, keyword: str, location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        self.logger.info(f"Initiating job retrieval for keyword: '{keyword}'...")
        jobs_data = []

        # Example remote JSON feed parsing (e.g., Remotive / public APIs for live data fallback)
        try:
            url = f"https://remotive.com/api/remote-jobs?search={keyword}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                raw_jobs = data.get("jobs", [])[:limit]

                for item in raw_jobs:
                    # Clean HTML tags from description
                    clean_desc = BeautifulSoup(item.get("description", ""), "html.parser").get_text(separator=" ")
                    
                    jobs_data.append({
                        "title": item.get("title", "").strip(),
                        "company": item.get("company_name", "").strip(),
                        "location": item.get("candidate_required_location", location or "Remote"),
                        "description": clean_desc.strip(),
                        "source_url": item.get("url", ""),
                        "source_platform": self.platform_name,
                        "is_remote": True,
                        "salary_min": None,
                        "salary_max": None,
                        "job_type": item.get("job_type", "Full-Time")
                    })
                self.logger.info(f"Successfully fetched {len(jobs_data)} jobs from public feed.")
        except Exception as e:
            self.logger.error(f"Error fetching job feed: {str(e)}")

        return jobs_data