"""
Data Services Module

This module contains services for database operations, data generation,
and data management for the TailWagg analytics platform.
"""

from .create_schema import main as create_database_schema
from .generate_data import main as generate_sample_data

__all__ = [
    "create_database_schema",
    "generate_sample_data"
]
