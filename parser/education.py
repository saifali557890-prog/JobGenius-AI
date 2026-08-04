import re
from typing import Optional
from utils.logger import get_logger

logger = get_logger("EducationExtractor")

EDUCATION_LEVELS = {
    "PhD / Doctorate": [r'\bph\.?d\b', r'\bdoctorate\b', r'\bdoctor of philosophy\b'],
    "Master's Degree": [r'\bmaster\b', r'\bms\b', r'\bm\.sc\b', r'\bmtech\b', r'\bmba\b', r'\bpost graduate\b'],
    "Bachelor's Degree": [r'\bbachelor\b', r'\bbs\b', r'\bb\.sc\b', r'\bbtech\b', r'\bbe\b', r'\bundergraduate\b'],
    "Diploma / Associate": [r'\bdiploma\b', r'\bassociate\b', r'\bhssc\b', r'\bintermediate\b']
}

class EducationExtractor:
    @staticmethod
    def extract_highest_education(text: str) -> Optional[str]:
        """
        Parses highest academic degree reached based on degree taxonomy hierarchy.
        """
        if not text:
            return "Not Specified"

        text_lower = text.lower()
        
        for level, patterns in EDUCATION_LEVELS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    logger.info(f"Detected education level: {level}")
                    return level
                    
        return "Bachelor's Degree" # Default standard domain threshold