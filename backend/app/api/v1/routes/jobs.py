"""
Job Description API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database.connection import get_db
from app.models.models import User, JobDescription
from app.models.schemas import JobDescriptionCreate, JobDescriptionResponse
from app.services.auth_service import get_current_user


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_job_description(
    job_data: JobDescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job description"""
    
    job = JobDescription(
        user_id=current_user.id,
        title=job_data.title,
        description=job_data.description
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    logger.info(f"Job description created: {job.id} by user {current_user.id}")
    
    return job


@router.get("/", response_model=List[JobDescriptionResponse])
async def list_job_descriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all job descriptions for current user"""
    jobs = db.query(JobDescription).filter(
        JobDescription.user_id == current_user.id
    ).order_by(JobDescription.created_at.desc()).all()
    
    return jobs


@router.get("/{job_id}", response_model=JobDescriptionResponse)
async def get_job_description(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific job description"""
    
    job = db.query(JobDescription).filter(
        JobDescription.id == job_id,
        JobDescription.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    return job


@router.put("/{job_id}", response_model=JobDescriptionResponse)
async def update_job_description(
    job_id: int,
    job_data: JobDescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a job description"""
    
    job = db.query(JobDescription).filter(
        JobDescription.id == job_id,
        JobDescription.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    job.title = job_data.title
    job.description = job_data.description
    db.commit()
    db.refresh(job)
    
    logger.info(f"Job description updated: {job.id}")
    
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_description(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a job description"""
    
    job = db.query(JobDescription).filter(
        JobDescription.id == job_id,
        JobDescription.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found"
        )
    
    db.delete(job)
    db.commit()
    
    logger.info(f"Job description deleted: {job_id}")
