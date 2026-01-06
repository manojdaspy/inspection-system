"""
Logging utility - Structured logging for inspection system
"""

import logging
import sys
from typing import Optional


# Global logger configuration
_loggers = {}
_log_level = logging.INFO


def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Setup and return a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        level: Optional logging level override
        
    Returns:
        Configured logger instance
    """
    if name in _loggers:
        return _loggers[name]
        
    logger = logging.getLogger(name)
    logger.setLevel(level or _log_level)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level or _log_level)
        
        # Format: timestamp - name - level - message
        formatter = logging.Formatter(
            '%(asctime)s - %(name)-30s - %(levelname)-8s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    _loggers[name] = logger
    return logger


def set_log_level(level: int) -> None:
    """
    Set global log level for all loggers.
    
    Args:
        level: Logging level (logging.DEBUG, INFO, WARNING, ERROR)
    """
    global _log_level
    _log_level = level
    
    for logger in _loggers.values():
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)