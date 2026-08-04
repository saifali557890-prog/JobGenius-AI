from sqlalchemy.orm import Session
from database.models import Job, Skill, User, Resume, Recommendation
from database.schemas import JobCreate, UserCreate
from utils.logger import get_logger
from typing import List, Optional

logger = get_logger("DatabaseQueries")

# --- Job Management Operations ---
def create_job(db: Session, job_data: JobCreate) -> Job:
    """Inserts a new job listing into the database along with skill associations."""
    try:
        # Check if job already exists by source_url
        if job_data.source_url:
            existing_job = db.query(Job).filter(Job.source_url == job_data.source_url).first()
            if existing_job:
                return existing_job

        db_job = Job(
            title=job_data.title,
            company=job_data.company,
            location=job_data.location,
            is_remote=job_data.is_remote,
            job_type=job_data.job_type,
            experience_level=job_data.experience_level,
            min_experience_years=job_data.min_experience_years,
            salary_min=job_data.salary_min,
            salary_max=job_data.salary_max,
            currency=job_data.currency,
            description=job_data.description,
            source_url=job_data.source_url,
            source_platform=job_data.source_platform
        )

        # Handle skill mapping
        for skill_name in job_data.skills:
            skill = db.query(Skill).filter(Skill.name.ilike(skill_name.strip())).first()
            if not skill:
                skill = Skill(name=skill_name.strip())
                db.add(skill)
                db.flush()
            db_job.skills.append(skill)

        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating job: {str(e)}")
        raise e


def get_all_jobs(db: Session, limit: int = 100, offset: int = 0) -> List[Job]:
    """Retrieves all active jobs from database."""
    return db.query(Job).order_by(Job.created_at.desc()).offset(offset).limit(limit).all()


def get_job_by_id(db: Session, job_id: int) -> Optional[Job]:
    """Retrieves a single job by its ID."""
    return db.query(Job).filter(Job.id == job_id).first()


def get_total_jobs_count(db: Session) -> int:
    """Returns total active job postings count."""
    return db.query(Job).count()


# --- User Management Operations ---
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Gets user record by email address."""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_data: UserCreate, hashed_password: str) -> User:
    """Creates a new user record."""
    db_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user