from typing import Dict, Any, List
from recommendations.similarity import MetricCalculator
from utils.logger import get_logger

logger = get_logger("RankingEngine")

class CandidateProfile:
    def __init__(self, raw_text: str, skills: List[str], experience_years: float = 0.0, education: str = "Bachelor's Degree"):
        self.raw_text = raw_text
        self.skills = skills
        self.experience_years = experience_years
        self.education = education


class RankingEngine:
    def __init__(
        self,
        weight_semantic: float = 0.50,
        weight_skill: float = 0.35,
        weight_experience: float = 0.15
    ):
        self.w_semantic = weight_semantic
        self.w_skill = weight_skill
        self.w_exp = weight_experience

    def rank_job(self, candidate: CandidateProfile, job, semantic_score: float) -> Dict[str, Any]:
        """
        Ranks a single job against candidate profile using weighted multi-criteria logic.
        """
        job_skill_names = [s.name for s in job.skills] if job.skills else []
        
        # 1. Skill Match Score & Skill Gap Analysis
        skill_score, matching_skills, missing_skills = MetricCalculator.calculate_skill_overlap(
            candidate.skills, job_skill_names
        )

        # 2. Experience Match Score
        exp_score = MetricCalculator.calculate_experience_score(
            candidate.experience_years, job.min_experience_years
        )

        # 3. Normalized Weighted Final Match Score (0.0 to 1.0 -> converted to 0-100%)
        # Clip semantic score boundary between 0.0 and 1.0
        clamped_semantic = max(0.0, min(1.0, float(semantic_score)))
        
        final_score = (
            (self.w_semantic * clamped_semantic) +
            (self.w_skill * skill_score) +
            (self.w_exp * exp_score)
        )
        
        match_percentage = round(final_score * 100, 1)

        return {
            "job": job,
            "final_match_score": match_percentage,
            "semantic_score": round(clamped_semantic * 100, 1),
            "skill_match_score": round(skill_score * 100, 1),
            "exp_match_score": round(exp_score * 100, 1),
            "matching_skills": matching_skills,
            "missing_skills": missing_skills
        }