from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional
from datetime import datetime

# --- Skill Schemas ---
class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int
    class Config:
        from_attributes = True


# --- Job Schemas ---
class JobBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    is_remote: bool = False
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    min_experience_years: int = 0
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: str = "USD"
    description: str
    source_url: Optional[str] = None
    source_platform: str

class JobCreate(JobBase):
    skills: List[str] = []

class JobResponse(JobBase):
    id: int
    created_at: datetime
    skills: List[SkillResponse] = []

    class Config:
        from_attributes = True


# --- User Schemas ---
class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str = "user"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Recommendation Schemas ---
class RecommendationResponse(BaseModel):
    id: int
    job: JobResponse
    overall_match_score: float
    similarity_score: float
    skill_match_score: float
    exp_match_score: float
    generated_at: datetime

    class Config:
        from_attributes = True