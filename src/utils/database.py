"""
Database utilities for the TailWagg analytics platform.
"""

import os
import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
from ..config import DATABASE_URL, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from .validation import validate_environment

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_database_engine(echo: bool = False) -> Engine:
    """
    Create and return a SQLAlchemy database engine.
    
    Parameters:
    -----------
    echo : bool, optional
        Whether to echo SQL statements (default: False)
    
    Returns:
    --------
    Engine
        SQLAlchemy engine instance
    
    Raises:
    -------
    ValueError
        If required environment variables are missing
    """
    # Validate environment variables
    validate_environment()
    
    try:
        engine = create_engine(DATABASE_URL, echo=echo)
        # logger.info(f"Database engine created successfully for {DB_NAME} on {DB_HOST}:{DB_PORT}")
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


def test_connection(engine: Optional[Engine] = None) -> bool:
    """
    Test database connection.
    
    Parameters:
    -----------
    engine : Engine, optional
        Database engine to test. If None, creates a new one.
    
    Returns:
    --------
    bool
        True if connection successful, False otherwise
    """
    if engine is None:
        engine = get_database_engine()
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        # logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def get_connection_info() -> dict:
    """
    Get database connection information (without password).
    
    Returns:
    --------
    dict
        Connection information dictionary
    """
    return {
        "host": DB_HOST,
        "port": DB_PORT,
        "database": DB_NAME,
        "user": DB_USER,
        "url": DATABASE_URL.replace(DB_PASSWORD, "***")
    }
