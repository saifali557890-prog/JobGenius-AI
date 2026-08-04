import re
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger("JobCleanerPipeline")

class JobDataCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        # Remove excessive whitespace, non-printable characters, and HTML noise
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # ASCII normalization
        return text.strip()

    @classmethod
    def process_job(cls, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes and verifies mandatory job attributes."""
        title = cls.clean_text(raw_job.get("title", "Software Engineer"))
        company = cls.clean_text(raw_job.get("company", "Unknown Company"))
        description = cls.clean_text(raw_job.get("description", ""))
        location = cls.clean_text(raw_job.get("location", "Remote"))

        # Infer remote flag if keywords present in location or title
        is_remote = raw_job.get("is_remote", False)
        if "remote" in location.lower() or "remote" in title.lower():
            is_remote = True

        # Extract basic skills present in job description using rule matches
        from parser.skill_extractor import SkillExtractor
        extractor = SkillExtractor()
        extracted_skills = extractor.extract_skills(description)

        cleaned_job = {
            "title": title,
            "company": company,
            "location": location,
            "is_remote": is_remote,
            "job_type": raw_job.get("job_type", "Full-Time"),
            "experience_level": "Mid Level",  # Default baseline
            "min_experience_years": 2,
            "salary_min": raw_job.get("salary_min"),
            "salary_max": raw_job.get("salary_max"),
            "currency": "USD",
            "description": description,
            "source_url": raw_job.get("source_url"),
            "source_platform": raw_job.get("source_platform", "WebScraper"),
            "skills": extracted_skills
        }
        return cleaned_job

    @classmethod
    def clean_batch(cls, raw_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned_list = []
        seen_urls = set()

        for raw_j in raw_jobs:
            url = raw_j.get("source_url")
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)

            processed = cls.process_job(raw_j)
            if len(processed["description"]) > 20:  # Valid description check
                cleaned_list.append(processed)

        logger.info(f"Cleaned batch: Retained {len(cleaned_list)} out of {len(raw_jobs)} raw jobs.")
        return cleaned_list