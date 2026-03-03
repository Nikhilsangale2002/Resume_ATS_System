"""
FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database.connection import engine, Base
from app.api.v1.routes import auth, resume, score, jobs, monitoring
from app.core.logging_config import setup_logging
from app.core.error_handlers import setup_exception_handlers, ErrorHandlingMiddleware
from app.core.rate_limiter import RateLimitMiddleware


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting ATS System API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ATS System API...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade ATS Resume Scoring System",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup exception handlers
setup_exception_handlers(app)

# Add middlewares (order matters - first added = last executed)
# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Error handling middleware
app.add_middleware(ErrorHandlingMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
)

# Include API routers with versioning
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(resume.router, prefix=f"{settings.API_V1_PREFIX}/resume", tags=["Resume"])
app.include_router(score.router, prefix=f"{settings.API_V1_PREFIX}/score", tags=["Scoring"])
app.include_router(jobs.router, prefix=f"{settings.API_V1_PREFIX}/jobs", tags=["Job Descriptions"])
app.include_router(monitoring.router, prefix=f"{settings.API_V1_PREFIX}/monitoring", tags=["Monitoring"])


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
