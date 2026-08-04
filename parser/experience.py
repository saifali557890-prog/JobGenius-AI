import re
from datetime import datetime
from utils.logger import get_logger

logger = get_logger("ExperienceExtractor")

class ExperienceExtractor:
    @staticmethod
    def extract_experience_years(text: str) -> float:
        """
        Extracts total work experience in years using numerical patterns and date ranges.
        """
        if not text:
            return 0.0

        # Pattern 1: Explicit mentions like "5+ years of experience", "3 yrs experience"
        explicit_patterns = [
            r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
            r'experience\s*(?:of\s*)?:?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)'
        ]

        for pattern in explicit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Return maximum explicit experience mentioned
                years = [float(m) for m in matches]
                logger.info(f"Explicit experience extracted: {max(years)} years.")
                return max(years)

        # Pattern 2: Extract date ranges like "2019 - 2023", "2020 to Present"
        date_pattern = r'(\b20\d{2}\b|\b19\d{2}\b)\s*(?:-|–|to)\s*(\b20\d{2}\b|\b19\d{2}\b|present|current|now)'
        date_matches = re.findall(date_pattern, text, re.IGNORECASE)

        total_months = 0
        current_year = datetime.now().year

        for start, end in date_matches:
            start_year = int(start)
            end_year = current_year if end.lower() in ['present', 'current', 'now'] else int(end)
            
            diff = end_year - start_year
            if 0 <= diff <= 45:  # Valid working lifespan constraint
                total_months += diff * 12

        estimated_years = round(total_months / 12.0, 1)
        logger.info(f"Calculated date range experience: {estimated_years} years.")
        return estimated_years