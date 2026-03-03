"""
Monitoring and Health Check Endpoints
Provides system health, metrics, and status information
"""
import os
import time
import platform
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis

from app.database.connection import get_db
from app.config import settings
from app.services.auth_service import get_current_user
from app.models.models import User, Resume, ATSScore

logger = logging.getLogger(__name__)

router = APIRouter()

# Track startup time
_startup_time = datetime.utcnow()


def get_redis_client():
    """Get Redis client for health checks"""
    try:
        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        return client
    except Exception:
        return None


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    Returns 200 if the service is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/health/live")
async def liveness_check():
    """
    Kubernetes liveness probe
    Returns 200 if the application is alive
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Kubernetes readiness probe
    Checks if all dependencies are available
    """
    checks = {
        "database": False,
        "redis": False
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis
    try:
        redis_client = get_redis_client()
        if redis_client and redis_client.ping():
            checks["redis"] = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
    
    # Determine overall status
    all_healthy = all(checks.values())
    
    if not all_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "checks": checks
            }
        )
    
    return {
        "status": "ready",
        "checks": checks
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with component status
    """
    components = {}
    
    # Database check
    db_start = time.time()
    try:
        db.execute(text("SELECT 1"))
        db_latency = (time.time() - db_start) * 1000
        components["database"] = {
            "status": "healthy",
            "latency_ms": round(db_latency, 2),
            "host": settings.MYSQL_HOST
        }
    except Exception as e:
        components["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Redis check
    redis_start = time.time()
    try:
        redis_client = get_redis_client()
        if redis_client:
            redis_client.ping()
            redis_latency = (time.time() - redis_start) * 1000
            info = redis_client.info("memory")
            components["redis"] = {
                "status": "healthy",
                "latency_ms": round(redis_latency, 2),
                "host": settings.REDIS_HOST,
                "used_memory": info.get("used_memory_human", "unknown")
            }
        else:
            components["redis"] = {"status": "unavailable"}
    except Exception as e:
        components["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Disk check
    try:
        disk = psutil.disk_usage("/")
        components["disk"] = {
            "status": "healthy" if disk.percent < 90 else "warning",
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent_used": disk.percent
        }
    except Exception as e:
        components["disk"] = {"status": "unknown", "error": str(e)}
    
    # Memory check
    try:
        memory = psutil.virtual_memory()
        components["memory"] = {
            "status": "healthy" if memory.percent < 90 else "warning",
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "percent_used": memory.percent
        }
    except Exception as e:
        components["memory"] = {"status": "unknown", "error": str(e)}
    
    # Overall status
    unhealthy = any(c.get("status") == "unhealthy" for c in components.values())
    warning = any(c.get("status") == "warning" for c in components.values())
    
    overall_status = "unhealthy" if unhealthy else ("warning" if warning else "healthy")
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "components": components
    }


@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    """
    Application metrics endpoint
    Returns key metrics for monitoring
    """
    metrics = {}
    
    # Uptime
    uptime = datetime.utcnow() - _startup_time
    metrics["uptime_seconds"] = int(uptime.total_seconds())
    metrics["uptime_human"] = str(uptime).split(".")[0]
    
    # Database counts
    try:
        metrics["users_count"] = db.query(User).count()
        metrics["resumes_count"] = db.query(Resume).count()
        metrics["scores_count"] = db.query(ATSScore).count()
        
        # Recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(hours=24)
        metrics["scores_24h"] = db.query(ATSScore).filter(
            ATSScore.created_at >= yesterday
        ).count()
        
        # Average score
        from sqlalchemy import func
        avg_score = db.query(func.avg(ATSScore.total_score)).scalar()
        metrics["average_score"] = round(float(avg_score or 0), 2)
        
    except Exception as e:
        logger.error(f"Error getting database metrics: {e}")
        metrics["database_error"] = str(e)
    
    # System metrics
    try:
        metrics["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        metrics["memory_percent"] = psutil.virtual_memory().percent
        metrics["disk_percent"] = psutil.disk_usage("/").percent
    except Exception:
        pass
    
    # Process metrics
    try:
        process = psutil.Process()
        metrics["process_memory_mb"] = round(process.memory_info().rss / (1024**2), 2)
        metrics["process_threads"] = process.num_threads()
    except Exception:
        pass
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "metrics": metrics
    }


@router.get("/info")
async def system_info():
    """
    System information endpoint
    """
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "hostname": platform.node(),
        "startup_time": _startup_time.isoformat(),
        "uptime_seconds": int((datetime.utcnow() - _startup_time).total_seconds()),
        "api_prefix": settings.API_V1_PREFIX,
        "features": {
            "authentication": True,
            "rate_limiting": True,
            "background_tasks": True,
            "file_upload": True
        }
    }


@router.get("/stats/summary")
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin statistics endpoint (requires authentication)
    """
    from sqlalchemy import func
    
    # Get time ranges
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    stats = {
        "totals": {
            "users": db.query(User).count(),
            "resumes": db.query(Resume).count(),
            "analyses": db.query(ATSScore).count()
        },
        "period": {
            "analyses_today": db.query(ATSScore).filter(ATSScore.created_at >= today).count(),
            "analyses_week": db.query(ATSScore).filter(ATSScore.created_at >= week_ago).count(),
            "analyses_month": db.query(ATSScore).filter(ATSScore.created_at >= month_ago).count(),
            "new_users_week": db.query(User).filter(User.created_at >= week_ago).count(),
        },
        "scores": {
            "average": round(float(db.query(func.avg(ATSScore.total_score)).scalar() or 0), 2),
            "highest": float(db.query(func.max(ATSScore.total_score)).scalar() or 0),
            "lowest": float(db.query(func.min(ATSScore.total_score)).scalar() or 0),
        },
        "grade_distribution": {}
    }
    
    # Grade distribution
    grades = db.query(
        ATSScore.grade, 
        func.count(ATSScore.id)
    ).group_by(ATSScore.grade).all()
    
    for grade, count in grades:
        if grade:
            stats["grade_distribution"][grade] = count
    
    return stats
