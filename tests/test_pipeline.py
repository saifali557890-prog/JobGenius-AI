import pytest
import numpy as np
from parser.skill_extractor import SkillExtractor
from parser.experience import ExperienceExtractor
from recommendation.similarity import MetricCalculator
from recommendation.ranking import RankingEngine, CandidateProfile

def test_skill_extraction():
    sample_text = "Senior Software Engineer with 5 years experience in Python, FastAPI, Docker, and PostgreSQL."
    extractor = SkillExtractor()
    skills = extractor.extract_skills(sample_text)
    
    assert "python" in skills
    assert "fastapi" in skills
    assert "docker" in skills

def test_experience_extraction():
    sample_text = "I have over 6 years of hands-on software development experience."
    exp = ExperienceExtractor.extract_experience_years(sample_text)
    assert exp == 6.0

def test_skill_overlap_metric():
    cand_skills = ["python", "sql", "docker"]
    job_skills = ["python", "sql", "aws", "kubernetes"]
    
    score, matching, missing = MetricCalculator.calculate_skill_overlap(cand_skills, job_skills)
    
    assert score == 0.5  # 2 out of 4 skills match
    assert "python" in matching
    assert "aws" in missing

def test_ranking_engine():
    cand = CandidateProfile(
        raw_text="Python Developer",
        skills=["python", "django", "sql"],
        experience_years=4.0
    )
    
    class FakeJob:
        title = "Python Backend Dev"
        skills = [type('Skill', (), {'name': 'python'}), type('Skill', (), {'name': 'django'})]
        min_experience_years = 3

    engine = RankingEngine()
    result = engine.rank_job(cand, FakeJob(), semantic_score=0.85)
    
    assert result["final_match_score"] > 50.0
    assert result["skill_match_score"] == 100.0