"""
Resume API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
import os
import uuid
import logging
import json
from decimal import Decimal
from datetime import datetime, timedelta

from app.database.connection import get_db
from app.models.models import User, Resume, ResumeSection, SectionType, ATSScore
from app.models.schemas import (
    ResumeResponse, ResumeDetailResponse,
    StandaloneATSScoreResponse, StandaloneScoreDetailsResponse,
    SuggestionResponse, IssueResponse, DetectedSkillsResponse, OptimizedResumeResponse,
    AnalysisHistoryItem, AnalysisHistoryResponse, DashboardStatsResponse
)
from app.services.auth_service import get_current_user, get_optional_current_user
from app.services.parser_service import ResumeParser, check_ats_format
from app.services.standalone_scorer import StandaloneATSScorer
from app.config import settings


router = APIRouter()
logger = logging.getLogger(__name__)

# Singleton scorer
_standalone_scorer = None

def get_scorer():
    global _standalone_scorer
    if _standalone_scorer is None:
        _standalone_scorer = StandaloneATSScorer()
    return _standalone_scorer


@router.post("/analyze-direct", response_model=StandaloneATSScoreResponse)
async def analyze_resume_direct(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze resume in one step.
    - Without auth: Returns analysis only (not saved)
    - With auth: Returns analysis AND saves to history
    """
    import traceback
    
    user_info = f"user={current_user.id}" if current_user else "anonymous"
    logger.info(f"=== Starting analyze-direct for file: {file.filename} ({user_info}) ===")
    
    try:
        # Validate file type
        file_extension = file.filename.split(".")[-1].lower()
        logger.info(f"File extension: {file_extension}")
        
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            logger.error(f"Invalid file extension: {file_extension}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Read file content
        file_bytes = await file.read()
        logger.info(f"File size: {len(file_bytes)} bytes")
        
        # Check file size
        if len(file_bytes) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            logger.error(f"File too large: {len(file_bytes)} bytes")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        # Parse resume
        logger.info("Starting resume parsing...")
        parser = ResumeParser()
        parsed = parser.parse(file_bytes, file_extension)
        logger.info(f"Parsing result keys: {parsed.keys() if parsed else 'None'}")
        
        if "error" in parsed:
            logger.error(f"Parse error: {parsed['error']}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=parsed["error"]
            )
        
        # Get sections
        resume_sections = parsed.get("sections", {})
        resume_text = parsed.get("text", "")
        logger.info(f"Extracted text length: {len(resume_text)} chars")
        logger.info(f"Sections found: {list(resume_sections.keys())}")
        
        # Analyze with standalone scorer
        logger.info("Starting ATS scoring...")
        scorer = get_scorer()
        result = scorer.analyze_resume(
            resume_text=resume_text,
            resume_sections=resume_sections,
            file_format=file_extension
        )
        logger.info(f"Scoring completed. Result keys: {result.keys()}")
        
        logger.info(f"Direct analysis completed: {result['total_score']}% for file {file.filename}")
        
        # Save to DB if user is authenticated
        if current_user:
            try:
                # Create resume record
                resume_record = Resume(
                    user_id=current_user.id,
                    file_name=file.filename,
                    parsed_text=resume_text[:10000],  # Limit text size
                    format_ok=True
                )
                db.add(resume_record)
                db.flush()  # Get the ID
                
                # Create ATS score record
                score_record = ATSScore(
                    resume_id=resume_record.id,
                    job_id=None,  # Standalone analysis
                    total_score=Decimal(str(result["total_score"])),
                    grade=result["grade"],
                    summary=result["summary"],
                    score_details=result["score_details"],
                    detected_skills=result["detected_skills"],
                    suggestions=result["suggestions"],
                    issues=result["issues"],
                    is_standalone=True
                )
                db.add(score_record)
                db.commit()
                
                logger.info(f"Saved analysis to DB: resume_id={resume_record.id}, score_id={score_record.id}")
            except Exception as db_error:
                logger.error(f"Failed to save to DB: {db_error}")
                db.rollback()
                # Continue without saving - don't fail the request
        
        # Build response
        logger.info("Building response...")
        response = StandaloneATSScoreResponse(
            total_score=result["total_score"],
            grade=result["grade"],
            summary=result["summary"],
            score_details=StandaloneScoreDetailsResponse(**result["score_details"]),
            issues=[IssueResponse(**issue) for issue in result["issues"]],
            suggestions=[SuggestionResponse(**sug) for sug in result["suggestions"]],
            detected_skills=DetectedSkillsResponse(**result["detected_skills"]),
            optimized_resume=OptimizedResumeResponse(**result["optimized_resume"])
        )
        logger.info("=== analyze-direct SUCCESS ===")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"=== analyze-direct FAILED ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Processing error: {str(e)}"
        )


@router.get("/history", response_model=AnalysisHistoryResponse)
async def get_analysis_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    sort_by: str = Query("newest", regex="^(newest|oldest|highest|lowest)$"),
    grade_filter: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analysis history for current user"""
    
    # Build query
    query = db.query(ATSScore, Resume).join(
        Resume, ATSScore.resume_id == Resume.id
    ).filter(
        Resume.user_id == current_user.id
    )
    
    # Apply grade filter
    if grade_filter and grade_filter != "all":
        query = query.filter(ATSScore.grade == grade_filter)
    
    # Apply sorting
    if sort_by == "newest":
        query = query.order_by(desc(ATSScore.created_at))
    elif sort_by == "oldest":
        query = query.order_by(ATSScore.created_at)
    elif sort_by == "highest":
        query = query.order_by(desc(ATSScore.total_score))
    elif sort_by == "lowest":
        query = query.order_by(ATSScore.total_score)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    results = query.offset(offset).limit(per_page).all()
    
    # Build response items
    items = []
    for score, resume in results:
        items.append(AnalysisHistoryItem(
            id=score.id,
            file_name=resume.file_name or "Unknown",
            total_score=float(score.total_score) if score.total_score else 0,
            grade=score.grade or "N/A",
            summary=score.summary,
            created_at=score.created_at,
            is_standalone=score.is_standalone if score.is_standalone is not None else True
        ))
    
    return AnalysisHistoryResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/dashboard-stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for current user"""
    
    # Get all scores for user
    scores_query = db.query(ATSScore).join(
        Resume, ATSScore.resume_id == Resume.id
    ).filter(Resume.user_id == current_user.id)
    
    all_scores = scores_query.all()
    
    # Calculate stats
    resumes_analyzed = len(all_scores)
    
    if resumes_analyzed > 0:
        total_score_sum = sum(float(s.total_score) for s in all_scores if s.total_score)
        average_score = round(total_score_sum / resumes_analyzed, 1)
    else:
        average_score = 0
    
    # Count optimized resumes (scores >= 70)
    optimized_resumes = sum(1 for s in all_scores if s.total_score and float(s.total_score) >= 70)
    
    # Estimate issues fixed (based on suggestions count)
    issues_fixed = 0
    for s in all_scores:
        if s.issues:
            try:
                issues_fixed += len(s.issues) if isinstance(s.issues, list) else 0
            except:
                pass
    
    # Score distribution by grade
    score_distribution = {"A+": 0, "A": 0, "B+": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for s in all_scores:
        if s.grade and s.grade in score_distribution:
            score_distribution[s.grade] += 1
    
    # Recent trend (last 7 days)
    recent_trend = []
    for i in range(6, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        day_scores = [
            float(s.total_score) for s in all_scores 
            if s.created_at and s.created_at.date() == date.date() and s.total_score
        ]
        avg = round(sum(day_scores) / len(day_scores), 1) if day_scores else 0
        recent_trend.append({"date": date_str, "score": avg, "count": len(day_scores)})
    
    return DashboardStatsResponse(
        resumes_analyzed=resumes_analyzed,
        average_score=average_score,
        optimized_resumes=optimized_resumes,
        issues_fixed=issues_fixed,
        score_distribution=score_distribution,
        recent_trend=recent_trend
    )


@router.delete("/history/{score_id}")
async def delete_analysis(
    score_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an analysis from history"""
    
    # Find the score and verify ownership
    score = db.query(ATSScore).join(
        Resume, ATSScore.resume_id == Resume.id
    ).filter(
        ATSScore.id == score_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Get resume to delete it too
    resume_id = score.resume_id
    
    # Delete score
    db.delete(score)
    
    # Delete resume if no other scores reference it
    other_scores = db.query(ATSScore).filter(
        ATSScore.resume_id == resume_id,
        ATSScore.id != score_id
    ).count()
    
    if other_scores == 0:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            db.delete(resume)
    
    db.commit()
    
    return {"message": "Analysis deleted successfully"}


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and parse a resume"""
    
    # Validate file type
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Read file content
    file_bytes = await file.read()
    
    # Check file size
    if len(file_bytes) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, "resumes", unique_filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    
    # Parse resume
    parser = ResumeParser()
    parsed = parser.parse(file_bytes, file_extension)
    
    if "error" in parsed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=parsed["error"]
        )
    
    # Check ATS format
    format_check = check_ats_format(parsed["text"], file_bytes)
    
    # Create resume record
    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=file_path,
        parsed_text=parsed["text"],
        format_ok=format_check["is_ats_friendly"]
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    # Save sections
    for section_name, content in parsed.get("sections", {}).items():
        try:
            section_type = SectionType[section_name]
            section = ResumeSection(
                resume_id=resume.id,
                section_type=section_type,
                content_json={
                    "text": content,
                    "contact": parsed.get("contact", {})
                }
            )
            db.add(section)
        except KeyError:
            logger.warning(f"Unknown section type: {section_name}")
    
    db.commit()
    
    logger.info(f"Resume uploaded: {resume.id} by user {current_user.id}")
    
    return resume


@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all resumes for current user"""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resume details"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Delete file
    if resume.file_path and os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    # Delete sections
    db.query(ResumeSection).filter(ResumeSection.resume_id == resume_id).delete()
    
    # Delete resume
    db.delete(resume)
    db.commit()
    
    logger.info(f"Resume deleted: {resume_id}")


@router.get("/{resume_id}/format-check")
async def check_resume_format(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check resume ATS format compatibility"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Read file and check format
    if resume.file_path and os.path.exists(resume.file_path):
        with open(resume.file_path, "rb") as f:
            file_bytes = f.read()
        format_check = check_ats_format(resume.parsed_text, file_bytes)
    else:
        format_check = check_ats_format(resume.parsed_text)
    
    return format_check
