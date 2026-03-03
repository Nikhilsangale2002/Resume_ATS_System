"""
Pydantic Schemas for API
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ================== Auth Schemas ==================

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ================== Resume Schemas ==================

class ResumeUpload(BaseModel):
    file_name: str


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_path: Optional[str]
    format_ok: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResumeSectionResponse(BaseModel):
    id: int
    section_type: str
    content_json: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class ResumeDetailResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    parsed_text: Optional[str]
    format_ok: bool
    created_at: datetime
    sections: List[ResumeSectionResponse] = []
    
    class Config:
        from_attributes = True


# ================== Job Description Schemas ==================

class JobDescriptionCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=50)


class JobDescriptionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ================== Scoring Schemas ==================

class ScoreRequest(BaseModel):
    resume_id: int
    job_id: int


class StandaloneScoreRequest(BaseModel):
    """Request for standalone ATS analysis (no job description needed)"""
    resume_id: int


class SuggestionResponse(BaseModel):
    priority: str
    category: str
    issue: str
    suggestion: str
    impact: str


class IssueResponse(BaseModel):
    category: str
    severity: str
    issue: str
    suggestion: str
    impact_score: int


class OptimizedSectionResponse(BaseModel):
    contact: str = ""
    summary: str = ""
    skills: str = ""
    experience: str = ""
    education: str = ""


class OptimizedResumeResponse(BaseModel):
    sections: Dict[str, str] = {}
    improvements: List[str] = []
    template_suggestions: List[str] = []


class StandaloneScoreDetailsResponse(BaseModel):
    formatting: float = 0
    contact_info: float = 0
    skills_section: float = 0
    experience_section: float = 0
    education_section: float = 0
    keywords_density: float = 0
    readability: float = 0
    length_optimization: float = 0


class DetectedSkillsResponse(BaseModel):
    technical: List[str] = []
    soft: List[str] = []
    tools: List[str] = []


class StandaloneATSScoreResponse(BaseModel):
    """Response for standalone ATS analysis"""
    total_score: float
    grade: str
    summary: str
    score_details: StandaloneScoreDetailsResponse
    issues: List[IssueResponse] = []
    suggestions: List[SuggestionResponse] = []
    detected_skills: DetectedSkillsResponse
    optimized_resume: OptimizedResumeResponse
    
    class Config:
        from_attributes = True


class KeywordMatchResponse(BaseModel):
    keyword: str
    is_matched: bool
    category: str
    
    class Config:
        from_attributes = True


class ScoreDetailsResponse(BaseModel):
    technical: float = 0
    experience: float = 0
    education: float = 0
    certifications: float = 0
    soft_skills: float = 0
    semantic: float = 0
    format: float = 0


class ATSScoreResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    total_score: float
    score_details: ScoreDetailsResponse
    created_at: datetime
    matched_keywords: List[KeywordMatchResponse] = []
    missing_keywords: List[KeywordMatchResponse] = []
    suggestions: List[str] = []
    
    class Config:
        from_attributes = True


class ScoreHistoryResponse(BaseModel):
    scores: List[ATSScoreResponse]
    total: int


# ================== Task Schemas ==================

class TaskStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ================== History & Dashboard Schemas ==================

class AnalysisHistoryItem(BaseModel):
    """Single analysis history item"""
    id: int
    file_name: str
    total_score: float
    grade: str
    summary: Optional[str] = None
    created_at: datetime
    is_standalone: bool = True
    
    class Config:
        from_attributes = True


class AnalysisHistoryResponse(BaseModel):
    """Response for analysis history"""
    items: List[AnalysisHistoryItem]
    total: int
    page: int
    per_page: int


class DashboardStatsResponse(BaseModel):
    """Response for dashboard statistics"""
    resumes_analyzed: int
    average_score: float
    optimized_resumes: int
    issues_fixed: int
    score_distribution: Dict[str, int]  # {"A+": 5, "A": 10, "B": 8, ...}
    recent_trend: List[Dict[str, Any]]  # [{"date": "2024-01-01", "score": 75}, ...]
