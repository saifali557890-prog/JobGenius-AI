from typing import List, Tuple, Set
from utils.logger import get_logger

logger = get_logger("SimilarityMetrics")

class MetricCalculator:
    @staticmethod
    def calculate_skill_overlap(candidate_skills: List[str], job_skills: List[str]) -> Tuple[float, List[str], List[str]]:
        """
        Calculates Jaccard / Overlap similarity ratio for skills.
        Returns: (match_score_ratio, matching_skills, missing_skills)
        """
        if not job_skills:
            return 1.0, candidate_skills, []
            
        cand_set: Set[str] = set(s.lower().strip() for s in candidate_skills)
        job_set: Set[str] = set(s.lower().strip() for s in job_skills)

        matching = sorted(list(cand_set.intersection(job_set)))
        missing = sorted(list(job_set.difference(cand_set)))

        # Overlap score relative to required job skills
        match_score = len(matching) / len(job_set) if len(job_set) > 0 else 0.0
        return round(match_score, 4), matching, missing

    @staticmethod
    def calculate_experience_score(candidate_years: float, min_required_years: int) -> float:
        """
        Calculates experience compatibility ratio.
        Fully matches (1.0) if candidate meets or exceeds requirements.
        """
        if min_required_years <= 0:
            return 1.0
            
        if candidate_years >= min_required_years:
            return 1.0
        else:
            # Linear penalty ratio if candidate has less experience
            return round(max(0.2, candidate_years / float(min_required_years)), 4)