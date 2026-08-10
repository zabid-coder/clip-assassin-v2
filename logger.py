"""
Clip Assassin Logging Configuration
Structured logging with file and console output
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
import platform

from config import config


def setup_logging():
    """Configure application logging"""
    
    # Create logger
    logger = logging.getLogger("clip_assassin")
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(config.LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if configured)
    if config.LOG_FILE:
        log_path = Path(config.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add JSON formatter for structured logs (optional)
    try:
        import json_logging
        json_logging.init_fastapi(enable_json=True)
        json_logging.init_non_web_framework()
    except ImportError:
        pass  # json_logging not installed, skip JSON formatting
    
    return logger


def get_logger(name: str = "clip_assassin") -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


# Performance timing decorator
def log_execution_time(logger=None):
    """Decorator to log function execution time"""
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            log = logger or get_logger()
            start = time.time()
            log.info(f"Starting {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                log.info(f"Completed {func.__name__} in {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start
                log.error(f"Failed {func.__name__} after {duration:.2f}s: {str(e)}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            log = logger or get_logger()
            start = time.time()
            log.info(f"Starting {func.__name__}")
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                log.info(f"Completed {func.__name__} in {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start
                log.error(f"Failed {func.__name__} after {duration:.2f}s: {str(e)}")
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
