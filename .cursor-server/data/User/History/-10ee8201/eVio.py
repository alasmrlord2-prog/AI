"""
Unified Logging System - نظام تسجيل موحد
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
from app.utils.path_resolver import resolve_path

# Global logger instance
_logger: Optional[logging.Logger] = None

def get_logger(name: str = "ai-agent") -> logging.Logger:
    """
    Get or create a logger instance with unified configuration.
    
    Args:
        name: Logger name (usually module name)
    
    Returns:
        Configured logger instance
    """
    global _logger
    
    if _logger is None:
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (if logs directory exists)
        try:
            log_dir = resolve_path("logs")
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            log_file = Path(log_dir) / "app.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            # If path resolution fails, skip file logging
            pass
        
        _logger = logger
    
    return _logger

def log_error(error: Exception, context: Optional[str] = None) -> None:
    """
    Log an error with context.
    
    Args:
        error: Exception to log
        context: Additional context information
    """
    logger = get_logger()
    message = f"Error: {str(error)}"
    if context:
        message = f"{context} - {message}"
    logger.error(message, exc_info=True)

def log_info(message: str, context: Optional[str] = None) -> None:
    """
    Log an info message.
    
    Args:
        message: Message to log
        context: Additional context information
    """
    logger = get_logger()
    if context:
        message = f"{context} - {message}"
    logger.info(message)

def log_warning(message: str, context: Optional[str] = None) -> None:
    """
    Log a warning message.
    
    Args:
        message: Message to log
        context: Additional context information
    """
    logger = get_logger()
    if context:
        message = f"{context} - {message}"
    logger.warning(message)

def log_debug(message: str, context: Optional[str] = None) -> None:
    """
    Log a debug message.
    
    Args:
        message: Message to log
        context: Additional context information
    """
    logger = get_logger()
    if context:
        message = f"{context} - {message}"
    logger.debug(message)

