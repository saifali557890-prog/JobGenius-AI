from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from database.postgres import Base

# Many-to-Many Relationship Table for Job Skills
job_skills = Table(
    'job_skills',
    Base.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id', ondelete="CASCADE"), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete="CASCADE"), primary_key=True)
)

# Many-to-Many Relationship Table for Resume Skills
resume_skills = Table(
    'resume_skills',
    Base.metadata,
    Column('resume_id', Integer, ForeignKey('resumes.id', ondelete="CASCADE"), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete="CASCADE"), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # "user" or "admin"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = 'skills'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=True)  # e.g., "Programming", "Framework", "Soft Skill"

    def __repr__(self):
        return f"<Skill(name='{self.name}')>"


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    company = Column(String(150), nullable=False, index=True)
    location = Column(String(100), nullable=True, index=True)
    is_remote = Column(Boolean, default=False)
    job_type = Column(String(50), nullable=True)  # Full-time, Part-time, Contract
    experience_level = Column(String(50), nullable=True)  # Entry, Mid, Senior
    min_experience_years = Column(Integer, default=0)
    
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    
    description = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True, unique=True)
    source_platform = Column(String(50), nullable=False)  # "Indeed", "Rozee", "LinkedIn"
    
    posted_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    skills = relationship("Skill", secondary=job_skills, backref="jobs")
    recommendations = relationship("Recommendation", back_populates="job", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = 'resumes'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    
    extracted_text = Column(Text, nullable=True)
    domain_detected = Column(String(100), nullable=True)
    total_experience_years = Column(Float, default=0.0)
    education_level = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resumes")
    skills = relationship("Skill", secondary=resume_skills, backref="resumes")


class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete="CASCADE"), nullable=False)
    
    overall_match_score = Column(Float, nullable=False)  # e.g., 94.5%
    similarity_score = Column(Float, nullable=False)    # Semantic embedding match
    skill_match_score = Column(Float, nullable=False)     # Skill overlap match
    exp_match_score = Column(Float, nullable=False)       # Experience match
    
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="recommendations")
    job = relationship("Job", back_populates="recommendations")