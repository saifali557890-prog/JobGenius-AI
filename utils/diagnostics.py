import os
import faiss
from sqlalchemy.orm import Session
from database.postgres import db_manager
from database.models import Job, Skill
from config import config
from utils.logger import get_logger

logger = get_logger("SystemDiagnostics")

class DiagnosticsManager:
    @staticmethod
    def check_database_health(db: Session) -> dict:
        """Verifies PostgreSQL connectivity and table row counts."""
        try:
            total_jobs = db.query(Job).count()
            total_skills = db.query(Skill).count()
            return {
                "status": "Healthy",
                "connected": True,
                "total_jobs": total_jobs,
                "total_skills": total_skills
            }
        except Exception as e:
            logger.error(f"DB Diagnostic Error: {str(e)}")
            return {
                "status": "Error",
                "connected": False,
                "error": str(e)
            }

    @staticmethod
    def check_faiss_health() -> dict:
        """Checks FAISS Vector Database index file existence and loaded vector count."""
        index_path = str(config.FAISS_INDEX_PATH)
        mapping_path = index_path + ".map"
        
        if not os.path.exists(index_path):
            return {
                "status": "Warning",
                "exists": False,
                "vector_count": 0,
                "message": "FAISS index file not found. Rebuild index from Admin Panel."
            }

        try:
            index = faiss.read_index(index_path)
            return {
                "status": "Healthy",
                "exists": True,
                "vector_count": index.ntotal,
                "dimension": index.d
            }
        except Exception as e:
            logger.error(f"FAISS Diagnostic Error: {str(e)}")
            return {
                "status": "Error",
                "exists": False,
                "error": str(e)
            }