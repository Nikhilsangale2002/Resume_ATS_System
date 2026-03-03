"""
Global Error Handling Middleware for FastAPI
Provides consistent error responses and logging
"""
import logging
import traceback
import uuid
from typing import Callable, Union
from datetime import datetime

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standardized error response format"""
    
    @staticmethod
    def create(
        status_code: int,
        message: str,
        error_code: str = None,
        details: Union[dict, list] = None,
        error_id: str = None
    ) -> dict:
        return {
            "success": False,
            "error": {
                "code": error_code or f"ERR_{status_code}",
                "message": message,
                "details": details,
                "error_id": error_id or str(uuid.uuid4())[:8],
                "timestamp": datetime.utcnow().isoformat()
            }
        }


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for catching and handling all exceptions"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        error_id = str(uuid.uuid4())[:8]
        
        try:
            response = await call_next(request)
            return response
            
        except Exception as exc:
            # Log the full traceback
            logger.error(
                f"Unhandled exception [{error_id}] on {request.method} {request.url.path}: "
                f"{type(exc).__name__}: {str(exc)}\n{traceback.format_exc()}"
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse.create(
                    status_code=500,
                    message="An unexpected error occurred. Please try again later.",
                    error_code="INTERNAL_ERROR",
                    error_id=error_id
                )
            )


def setup_exception_handlers(app):
    """Setup all exception handlers for the FastAPI app"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle FastAPI HTTP exceptions"""
        error_id = str(uuid.uuid4())[:8]
        
        # Map status codes to error codes
        error_codes = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMITED",
            500: "INTERNAL_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
        }
        
        logger.warning(
            f"HTTP {exc.status_code} [{error_id}] on {request.method} {request.url.path}: {exc.detail}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.create(
                status_code=exc.status_code,
                message=str(exc.detail),
                error_code=error_codes.get(exc.status_code, f"HTTP_{exc.status_code}"),
                error_id=error_id
            ),
            headers=getattr(exc, "headers", None)
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors"""
        error_id = str(uuid.uuid4())[:8]
        
        # Format validation errors nicely
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"Validation error [{error_id}] on {request.method} {request.url.path}: {errors}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse.create(
                status_code=422,
                message="Request validation failed",
                error_code="VALIDATION_ERROR",
                details=errors,
                error_id=error_id
            )
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError):
        """Handle direct Pydantic validation errors"""
        error_id = str(uuid.uuid4())[:8]
        
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse.create(
                status_code=422,
                message="Data validation failed",
                error_code="VALIDATION_ERROR",
                details=errors,
                error_id=error_id
            )
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """Handle database errors"""
        error_id = str(uuid.uuid4())[:8]
        
        logger.error(
            f"Database error [{error_id}] on {request.method} {request.url.path}: "
            f"{type(exc).__name__}: {str(exc)}"
        )
        
        # Check for integrity errors (duplicate key, foreign key, etc.)
        if isinstance(exc, IntegrityError):
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=ErrorResponse.create(
                    status_code=409,
                    message="Data conflict. The resource may already exist.",
                    error_code="DATABASE_CONFLICT",
                    error_id=error_id
                )
            )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse.create(
                status_code=500,
                message="A database error occurred. Please try again later.",
                error_code="DATABASE_ERROR",
                error_id=error_id
            )
        )
    
    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(request: Request, exc: FileNotFoundError):
        """Handle file not found errors"""
        error_id = str(uuid.uuid4())[:8]
        
        logger.warning(f"File not found [{error_id}]: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse.create(
                status_code=404,
                message="The requested file was not found",
                error_code="FILE_NOT_FOUND",
                error_id=error_id
            )
        )
    
    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError):
        """Handle permission errors"""
        error_id = str(uuid.uuid4())[:8]
        
        logger.error(f"Permission error [{error_id}]: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse.create(
                status_code=403,
                message="Permission denied",
                error_code="PERMISSION_DENIED",
                error_id=error_id
            )
        )
    
    @app.exception_handler(TimeoutError)
    async def timeout_error_handler(request: Request, exc: TimeoutError):
        """Handle timeout errors"""
        error_id = str(uuid.uuid4())[:8]
        
        logger.error(f"Timeout error [{error_id}] on {request.url.path}")
        
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content=ErrorResponse.create(
                status_code=504,
                message="The request timed out. Please try again.",
                error_code="TIMEOUT",
                error_id=error_id
            )
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Catch-all handler for unhandled exceptions"""
        error_id = str(uuid.uuid4())[:8]
        
        logger.error(
            f"Unhandled exception [{error_id}] on {request.method} {request.url.path}: "
            f"{type(exc).__name__}: {str(exc)}\n{traceback.format_exc()}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse.create(
                status_code=500,
                message="An unexpected error occurred. Please try again later.",
                error_code="INTERNAL_ERROR",
                error_id=error_id
            )
        )


# Custom exceptions
class ATSException(Exception):
    """Base exception for ATS system"""
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        error_code: str = "ATS_ERROR",
        details: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(message)


class ResumeParsingError(ATSException):
    """Error parsing resume"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="RESUME_PARSING_ERROR",
            details=details
        )


class ScoringError(ATSException):
    """Error calculating score"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="SCORING_ERROR",
            details=details
        )


class AuthenticationError(ATSException):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(ATSException):
    """Authorization error"""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )
