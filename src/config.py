"""
Configuration settings for the TailWagg analytics platform.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "tailwagg")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Note: validate_environment() is available in src.utils.validation
# It is not imported here to avoid circular import issues

# Construct the connection string
if DB_PASSWORD:
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = None
    logger.warning("DB_PASSWORD not set. Database operations will fail.")

# Data Configuration
DATA_DIR = "data"
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
INTERIM_DATA_DIR = os.path.join(DATA_DIR, "interim")

# Reports Configuration
REPORTS_DIR = "reports"
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")

# Model Configuration
MODEL_DIR = "models"
MODEL_VERSION = "1.0.0"

# Visualization Configuration
PLOT_STYLE = "whitegrid"
PLOT_PALETTE = "muted"
FIGURE_SIZE = (10, 6)

# Analysis Configuration
ROLLING_WINDOWS = {
    "short_term": 30,  # days
    "long_term": 90    # days
}

PROMO_BASELINE_PERIODS = [14, 30, 60]  # days to look back for baseline

# Export configuration
__all__ = [
    "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD", "DATABASE_URL",
    "DATA_DIR", "RAW_DATA_DIR", "PROCESSED_DATA_DIR", "INTERIM_DATA_DIR",
    "REPORTS_DIR", "FIGURES_DIR", "MODEL_DIR", "MODEL_VERSION",
    "PLOT_STYLE", "PLOT_PALETTE", "FIGURE_SIZE",
    "ROLLING_WINDOWS", "PROMO_BASELINE_PERIODS"
]
