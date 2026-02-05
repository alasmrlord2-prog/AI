"""Custom exceptions for the application."""
from app.exceptions.base import (
    AppException,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    InternalServerError,
)
from app.exceptions.handlers import setup_exception_handlers

__all__ = [
    "AppException",
    "NotFoundError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "InternalServerError",
    "setup_exception_handlers",
]

