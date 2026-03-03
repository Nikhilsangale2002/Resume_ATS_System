"""
Scoring API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database.connection import get_db
from app.models.models import User, Resume, ResumeSection, JobDescription, ATSScore, Keyword, KeywordCategory
from app.models.schemas import (
    ScoreRequest, ATSScoreResponse, ScoreDetailsResponse, TaskResponse, TaskStatus,
    StandaloneScoreRequest, StandaloneATSScoreResponse, StandaloneScoreDetailsResponse,
    SuggestionResponse, IssueResponse, DetectedSkillsResponse, OptimizedResumeResponse
)
from app.services.auth_service import get_current_user
from app.services.scoring_engine import ATSScoringEngine
from app.services.standalone_scorer import StandaloneATSScorer
from app.services.parser_service import check_ats_format
from app.services.skill_normalizer import SkillNormalizer


router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize scoring engines (singleton)
scoring_engine = None
standalone_scorer = None


def get_scoring_engine():
    global scoring_engine
    if scoring_engine is None:
        scoring_engine = ATSScoringEngine()
    return scoring_engine


def get_standalone_scorer():
    global standalone_scorer
    if standalone_scorer is None:
        standalone_scorer = StandaloneATSScorer()
    return standalone_scorer


@router.post("/analyze", response_model=StandaloneATSScoreResponse)
async def analyze_resume_standalone(
    request: StandaloneScoreRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze resume for ATS compatibility WITHOUT a job description.
    Returns comprehensive analysis, suggestions, and optimized resume template.
    """
    
    # Get resume
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get resume sections
    sections = db.query(ResumeSection).filter(
        ResumeSection.resume_id == resume.id
    ).all()
    
    resume_sections = {}
    for section in sections:
        content = section.content_json.get("text", "") if section.content_json else ""
        resume_sections[section.section_type.value] = content
    
    # Get file format
    file_format = resume.file_name.split('.')[-1] if resume.file_name else "pdf"
    
    # Analyze with standalone scorer
    scorer = get_standalone_scorer()
    result = scorer.analyze_resume(
        resume_text=resume.parsed_text or "",
        resume_sections=resume_sections,
        file_format=file_format
    )
    
    logger.info(f"Standalone analysis completed for resume {resume.id}: {result['total_score']}%")
    
    # Build response
    return StandaloneATSScoreResponse(
        total_score=result["total_score"],
        grade=result["grade"],
        summary=result["summary"],
        score_details=StandaloneScoreDetailsResponse(**result["score_details"]),
        issues=[IssueResponse(**issue) for issue in result["issues"]],
        suggestions=[SuggestionResponse(**sug) for sug in result["suggestions"]],
        detected_skills=DetectedSkillsResponse(**result["detected_skills"]),
        optimized_resume=OptimizedResumeResponse(**result["optimized_resume"])
    )


@router.post("/calculate", response_model=ATSScoreResponse)
async def calculate_score(
    request: ScoreRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate ATS score for a resume against a job description"""
    
    # Get resume
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get job description
    job = db.query(JobDescription).filter(
        JobDescription.id == request.job_id,
        JobDescription.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    # Get resume sections
    sections = db.query(ResumeSection).filter(
        ResumeSection.resume_id == resume.id
    ).all()
    
    resume_sections = {}
    for section in sections:
        content = section.content_json.get("text", "") if section.content_json else ""
        resume_sections[section.section_type.value] = content
    
    # Check format score
    format_check = check_ats_format(resume.parsed_text)
    format_score = format_check["format_score"]
    
    # Calculate score
    engine = get_scoring_engine()
    scores, matched, missing, suggestions = engine.calculate_score(
        resume_text=resume.parsed_text or "",
        resume_sections=resume_sections,
        job_description=job.description,
        format_score=format_score
    )
    
    # Save score to database
    ats_score = ATSScore(
        resume_id=resume.id,
        job_id=job.id,
        total_score=scores.total,
        score_details=scores.to_dict()
    )
    db.add(ats_score)
    db.commit()
    db.refresh(ats_score)
    
    # Save keywords
    normalizer = SkillNormalizer(db)
    
    for kw in matched:
        normalized = normalizer.normalize(kw)
        keyword = Keyword(
            score_id=ats_score.id,
            keyword=normalized,
            is_matched=True,
            category=KeywordCategory.technical
        )
        db.add(keyword)
    
    for kw in missing:
        normalized = normalizer.normalize(kw)
        keyword = Keyword(
            score_id=ats_score.id,
            keyword=normalized,
            is_matched=False,
            category=KeywordCategory.technical
        )
        db.add(keyword)
    
    db.commit()
    
    logger.info(f"Score calculated: {ats_score.id} - {scores.total}%")
    
    # Build response
    return {
        "id": ats_score.id,
        "resume_id": resume.id,
        "job_id": job.id,
        "total_score": float(scores.total),
        "score_details": ScoreDetailsResponse(**scores.to_dict()),
        "created_at": ats_score.created_at,
        "matched_keywords": [{"keyword": kw, "is_matched": True, "category": "technical"} for kw in matched],
        "missing_keywords": [{"keyword": kw, "is_matched": False, "category": "technical"} for kw in missing],
        "suggestions": suggestions
    }


@router.get("/history", response_model=List[ATSScoreResponse])
async def get_score_history(
    resume_id: int = None,
    job_id: int = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get scoring history for user"""
    
    query = db.query(ATSScore).join(Resume).filter(Resume.user_id == current_user.id)
    
    if resume_id:
        query = query.filter(ATSScore.resume_id == resume_id)
    
    if job_id:
        query = query.filter(ATSScore.job_id == job_id)
    
    scores = query.order_by(ATSScore.created_at.desc()).limit(limit).all()
    
    results = []
    for score in scores:
        keywords = db.query(Keyword).filter(Keyword.score_id == score.id).all()
        matched = [{"keyword": k.keyword, "is_matched": True, "category": k.category.value} for k in keywords if k.is_matched]
        missing = [{"keyword": k.keyword, "is_matched": False, "category": k.category.value} for k in keywords if not k.is_matched]
        
        results.append({
            "id": score.id,
            "resume_id": score.resume_id,
            "job_id": score.job_id,
            "total_score": float(score.total_score),
            "score_details": ScoreDetailsResponse(**(score.score_details or {})),
            "created_at": score.created_at,
            "matched_keywords": matched,
            "missing_keywords": missing,
            "suggestions": []
        })
    
    return results


@router.get("/{score_id}", response_model=ATSScoreResponse)
async def get_score(
    score_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific score details"""
    
    score = db.query(ATSScore).join(Resume).filter(
        ATSScore.id == score_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not found"
        )
    
    keywords = db.query(Keyword).filter(Keyword.score_id == score.id).all()
    matched = [{"keyword": k.keyword, "is_matched": True, "category": k.category.value} for k in keywords if k.is_matched]
    missing = [{"keyword": k.keyword, "is_matched": False, "category": k.category.value} for k in keywords if not k.is_matched]
    
    return {
        "id": score.id,
        "resume_id": score.resume_id,
        "job_id": score.job_id,
        "total_score": float(score.total_score),
        "score_details": ScoreDetailsResponse(**(score.score_details or {})),
        "created_at": score.created_at,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "suggestions": []
    }


@router.delete("/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_score(
    score_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a score"""
    
    score = db.query(ATSScore).join(Resume).filter(
        ATSScore.id == score_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not found"
        )
    
    # Delete keywords
    db.query(Keyword).filter(Keyword.score_id == score_id).delete()
    
    # Delete score
    db.delete(score)
    db.commit()
    
    logger.info(f"Score deleted: {score_id}")
