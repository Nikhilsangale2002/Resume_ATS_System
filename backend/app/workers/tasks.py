"""
Celery Background Tasks
"""
import logging
from celery import shared_task
from sqlalchemy.orm import Session

from app.workers.celery_config import celery_app
from app.database.connection import SessionLocal
from app.services.parser_service import ResumeParser, check_ats_format
from app.services.scoring_engine import ATSScoringEngine
from app.services.skill_normalizer import SkillNormalizer
from app.models.models import Resume, ResumeSection, JobDescription, ATSScore, Keyword, KeywordCategory, SectionType


logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="parse_resume")
def parse_resume_task(self, resume_id: int, file_path: str, file_extension: str):
    """
    Background task to parse resume
    """
    logger.info(f"Starting parse_resume task for resume_id: {resume_id}")
    
    db = SessionLocal()
    try:
        # Read file
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        
        # Parse resume
        parser = ResumeParser()
        parsed = parser.parse(file_bytes, file_extension)
        
        if "error" in parsed:
            logger.error(f"Parse error: {parsed['error']}")
            return {"status": "error", "error": parsed["error"]}
        
        # Check format
        format_check = check_ats_format(parsed["text"], file_bytes)
        
        # Update resume in database
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            resume.parsed_text = parsed["text"]
            resume.format_ok = format_check["is_ats_friendly"]
            
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
                    pass
            
            db.commit()
        
        logger.info(f"Resume parsed successfully: {resume_id}")
        
        return {
            "status": "success",
            "resume_id": resume_id,
            "word_count": parsed.get("word_count", 0),
            "format_ok": format_check["is_ats_friendly"]
        }
        
    except Exception as e:
        logger.error(f"Parse resume error: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True, name="calculate_score")
def calculate_score_task(self, resume_id: int, job_id: int, user_id: int):
    """
    Background task to calculate ATS score
    """
    logger.info(f"Starting calculate_score task: resume={resume_id}, job={job_id}")
    
    db = SessionLocal()
    try:
        # Get resume
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return {"status": "error", "error": "Resume not found"}
        
        # Get job
        job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
        if not job:
            return {"status": "error", "error": "Job description not found"}
        
        # Get resume sections
        sections = db.query(ResumeSection).filter(ResumeSection.resume_id == resume_id).all()
        resume_sections = {}
        for section in sections:
            content = section.content_json.get("text", "") if section.content_json else ""
            resume_sections[section.section_type.value] = content
        
        # Check format
        format_check = check_ats_format(resume.parsed_text or "")
        
        # Calculate score
        engine = ATSScoringEngine()
        scores, matched, missing, suggestions = engine.calculate_score(
            resume_text=resume.parsed_text or "",
            resume_sections=resume_sections,
            job_description=job.description,
            format_score=format_check["format_score"]
        )
        
        # Save score
        ats_score = ATSScore(
            resume_id=resume_id,
            job_id=job_id,
            total_score=scores.total,
            score_details=scores.to_dict()
        )
        db.add(ats_score)
        db.commit()
        db.refresh(ats_score)
        
        # Save keywords
        normalizer = SkillNormalizer(db)
        
        for kw in matched:
            keyword = Keyword(
                score_id=ats_score.id,
                keyword=normalizer.normalize(kw),
                is_matched=True,
                category=KeywordCategory.technical
            )
            db.add(keyword)
        
        for kw in missing:
            keyword = Keyword(
                score_id=ats_score.id,
                keyword=normalizer.normalize(kw),
                is_matched=False,
                category=KeywordCategory.technical
            )
            db.add(keyword)
        
        db.commit()
        
        logger.info(f"Score calculated: {ats_score.id} = {scores.total}%")
        
        return {
            "status": "success",
            "score_id": ats_score.id,
            "total_score": scores.total,
            "score_details": scores.to_dict(),
            "matched_count": len(matched),
            "missing_count": len(missing),
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Calculate score error: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(name="batch_score_resumes")
def batch_score_resumes_task(resume_ids: list, job_id: int, user_id: int):
    """
    Background task to score multiple resumes against one job
    """
    results = []
    for resume_id in resume_ids:
        result = calculate_score_task(resume_id, job_id, user_id)
        results.append(result)
    
    return {
        "status": "success",
        "total": len(results),
        "results": results
    }
