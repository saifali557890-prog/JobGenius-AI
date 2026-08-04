from database.postgres import db_manager
from database.queries import create_job
from database.schemas import JobCreate
from scraper.generic_board import GenericBoardScraper
from preprocessing.clean_jobs import JobDataCleaner
from utils.logger import get_logger

logger = get_logger("ScraperOrchestrator")

class IngestionPipeline:
    def __init__(self):
        self.scraper = GenericBoardScraper()

    def run_pipeline(self, keyword: str = "python", limit: int = 15) -> int:
        """Fetches, cleans, and saves jobs directly into the database."""
        logger.info(f"Starting ingestion pipeline for target: '{keyword}'")
        raw_jobs = self.scraper.scrape(keyword=keyword, limit=limit)
        
        if not raw_jobs:
            logger.warning("No jobs retrieved during scraping.")
            return 0

        cleaned_jobs = JobDataCleaner.clean_batch(raw_jobs)
        
        saved_count = 0
        session = next(db_manager.get_session())

        for job_dict in cleaned_jobs:
            try:
                job_schema = JobCreate(**job_dict)
                create_job(session, job_schema)
                saved_count += 1
            except Exception as e:
                logger.error(f"Failed to save job '{job_dict.get('title')}': {str(e)}")

        logger.info(f"Ingestion Pipeline Completed. Total Jobs Saved/Updated: {saved_count}")
        return saved_count