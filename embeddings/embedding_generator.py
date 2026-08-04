import numpy as np
from typing import List, Tuple
from sqlalchemy.orm import Session
from database.models import Job
from embeddings.embedding_model import EmbeddingModel
from vector_db.faiss_manager import FAISSVectorManager
from utils.logger import get_logger

logger = get_logger("EmbeddingGenerator")

class JobEmbeddingPipeline:
    def __init__(self):
        self.encoder = EmbeddingModel()
        self.faiss_manager = FAISSVectorManager(dimension=self.encoder.embedding_dimension)

    def prepare_job_text(self, job: Job) -> str:
        """Combines job attributes into rich semantic text representation."""
        skills_text = ", ".join([s.name for s in job.skills]) if job.skills else ""
        structured_str = f"Job Title: {job.title}. Company: {job.company}. Required Skills: {skills_text}. Description: {job.description}"
        return structured_str

    def sync_database_embeddings(self, db: Session) -> int:
        """Reads all active jobs from SQL DB, generates vectors, and rebuilds FAISS Index."""
        jobs = db.query(Job).all()
        if not jobs:
            logger.warning("No jobs found in database to index.")
            return 0

        job_texts = []
        job_ids = []

        for job in jobs:
            text = self.prepare_job_text(job)
            job_texts.append(text)
            job_ids.append(job.id)

        logger.info(f"Generating embeddings for {len(job_texts)} database jobs...")
        vectors = self.encoder.encode(job_texts)
        
        # Build FAISS Index
        self.faiss_manager.build_index(vectors, job_ids)
        return len(job_ids)

    def search_similar_jobs(self, resume_text: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """Encodes user resume text and runs semantic search in FAISS Index."""
        resume_vector = self.encoder.encode([resume_text])
        results = self.faiss_manager.search(resume_vector, top_k=top_k)
        return results