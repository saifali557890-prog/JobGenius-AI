from abc import ABC, abstractmethod
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger("BaseScraper")

class BaseScraper(ABC):
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.logger = get_logger(f"Scraper_{platform_name}")

    @abstractmethod
    def scrape(self, keyword: str, location: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Scrapes job listings based on search criteria.
        Must return a list of standardized job dictionaries:
        [
            {
                "title": str,
                "company": str,
                "location": str,
                "description": str,
                "source_url": str,
                "source_platform": str,
                "is_remote": bool,
                "salary_min": float or None,
                "salary_max": float or None
            }, ...
        ]
        """
        pass