"""
Centralized error handling middleware for FastAPI
Provides consistent error responses across all endpoints
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error exception"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class NotFoundError(APIError):
    """Resource not found exception"""
    def __init__(self, message: str = "Resource not found", details: dict = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class UnauthorizedError(APIError):
    """Unauthorized access exception"""
    def __init__(self, message: str = "Unauthorized", details: dict = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class ForbiddenError(APIError):
    """Forbidden access exception"""
    def __init__(self, message: str = "Forbidden", details: dict = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


class ConflictError(APIError):
    """Resource conflict exception"""
    def __init__(self, message: str = "Resource conflict", details: dict = None):
        super().__init__(message, status.HTTP_409_CONFLICT, details)


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle custom API errors"""
    logger.error(f"API Error: {exc.message}", extra={
        "status_code": exc.status_code,
        "path": request.url.path,
        "details": exc.details
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "status_code": exc.status_code,
                "details": exc.details,
                "path": request.url.path
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions"""
    logger.warning(f"HTTP Exception: {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": request.url.path
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation Error: {errors}", extra={
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation failed",
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "details": {"validation_errors": errors},
                "path": request.url.path
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.exception("Unexpected error occurred", extra={
        "path": request.url.path,
        "exception_type": type(exc).__name__
    })
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An unexpected error occurred",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "path": request.url.path
            }
        }
    )


def setup_error_handlers(app):
    """Setup all error handlers for the FastAPI app"""
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

