"""
TailWagg - Pet Retail Analytics Platform

A comprehensive analytics platform for pet retail business intelligence,
featuring sales forecasting, promotional analysis, and product performance metrics.
"""

__version__ = "1.0.0"
__author__ = "Paul Rodriguez"
__email__ = "pdrfoto@gmail.com"

# Import configuration
from .config import *

# Note: Services are not imported by default to avoid dependency issues
# Import them explicitly when needed:
# from .services.create_schema import main as create_database_schema
# from .services.generate_data import main as generate_sample_data

__all__ = [
    "__version__",
    "__author__",
    "__email__"
]
