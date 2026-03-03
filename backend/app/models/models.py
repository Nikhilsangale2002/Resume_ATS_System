"""
Database Models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.connection import Base


class SectionType(enum.Enum):
    skills = "skills"
    experience = "experience"
    education = "education"
    certifications = "certifications"
    projects = "projects"
    summary = "summary"


class KeywordCategory(enum.Enum):
    technical = "technical"
    soft = "soft"
    education = "education"
    certification = "certification"


class SkillCategory(enum.Enum):
    frontend = "frontend"
    backend = "backend"
    devops = "devops"
    database = "database"
    mobile = "mobile"
    cloud = "cloud"
    other = "other"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    resumes = relationship("Resume", back_populates="user")
    job_descriptions = relationship("JobDescription", back_populates="user")


class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255))
    file_path = Column(String(500))
    parsed_text = Column(Text)
    format_ok = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    sections = relationship("ResumeSection", back_populates="resume")
    scores = relationship("ATSScore", back_populates="resume")


class ResumeSection(Base):
    __tablename__ = "resume_sections"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    section_type = Column(Enum(SectionType), nullable=False)
    content_json = Column(JSON)
    
    # Relationships
    resume = relationship("Resume", back_populates="sections")


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="job_descriptions")
    scores = relationship("ATSScore", back_populates="job")


class ATSScore(Base):
    __tablename__ = "ats_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=True)  # Nullable for standalone analysis
    total_score = Column(DECIMAL(5, 2))
    grade = Column(String(5))  # A+, A, B+, B, C, D, F
    summary = Column(Text)
    score_details = Column(JSON)
    # score_details format:
    # {
    #     "contact_info": {"score": 10, "max": 10},
    #     "formatting": {"score": 8, "max": 10},
    #     "skills": {"score": 15, "max": 20},
    #     ...
    # }
    detected_skills = Column(JSON)  # {"technical": [...], "soft": [...]}
    suggestions = Column(JSON)  # [{"category": "...", "suggestion": "..."}]
    issues = Column(JSON)  # [{"severity": "...", "issue": "..."}]
    is_standalone = Column(Boolean, default=True)  # True for standalone, False for job-match
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    resume = relationship("Resume", back_populates="scores")
    job = relationship("JobDescription", back_populates="scores")
    keywords = relationship("Keyword", back_populates="score")


class Keyword(Base):
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    score_id = Column(Integer, ForeignKey("ats_scores.id"), nullable=False)
    keyword = Column(String(100))
    is_matched = Column(Boolean, default=False)
    category = Column(Enum(KeywordCategory))
    
    # Relationships
    score = relationship("ATSScore", back_populates="keywords")


class SkillAlias(Base):
    __tablename__ = "skill_aliases"
    
    id = Column(Integer, primary_key=True, index=True)
    alias_name = Column(String(100), nullable=False, index=True)
    standard_name = Column(String(100), nullable=False)
    category = Column(Enum(SkillCategory))
