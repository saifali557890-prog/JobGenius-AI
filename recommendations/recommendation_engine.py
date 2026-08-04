from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.queries import get_job_by_id
from embeddings.embedding_generator import JobEmbeddingPipeline
from recommendations.ranking import RankingEngine, CandidateProfile
from utils.logger import get_logger

logger = get_logger("RecommendationEngine")

class RecommendationService:
    def __init__(self):
        self.embedding_pipeline = JobEmbeddingPipeline()
        self.ranking_engine = RankingEngine()

    def get_recommendations(
        self,
        db: Session,
        candidate_text: str,
        candidate_skills: List[str],
        candidate_exp: float = 0.0,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generates production-grade multi-criteria job recommendations for candidate.
        """
        logger.info("Executing Recommendation Pipeline...")
        
        # 1. FAISS Semantic Similarity Top Candidate Retrieval
        vector_results = self.embedding_pipeline.search_similar_jobs(candidate_text, top_k=top_k * 2)
        
        if not vector_results:
            logger.warning("No semantic candidates found in FAISS index.")
            return []

        candidate_profile = CandidateProfile(
            raw_text=candidate_text,
            skills=candidate_skills,
            experience_years=candidate_exp
        )

        ranked_recommendations = []

        # 2. Apply Multi-Criteria Scoring & Skill Gap Analysis
        for job_id, sem_score in vector_results:
            job = get_job_by_id(db, job_id)
            if job:
                match_data = self.ranking_engine.rank_job(candidate_profile, job, sem_score)
                ranked_recommendations.append(match_data)

        # 3. Sort by Final Hybrid Weighted Score (Highest Match First)
        ranked_recommendations.sort(key=lambda x: x["final_match_score"], reverse=True)
        
        top_matches = ranked_recommendations[:top_k]
        logger.info(f"Successfully generated top {len(top_matches)} job recommendations.")
        return top_matches