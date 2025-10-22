"""
Utility modules for the TailWagg analytics platform.
"""

from .database import get_database_engine, test_connection
from .validation import validate_environment, validate_dataframe
from .notebook_helpers import (
    setup_notebook_environment,
    load_data_with_validation,
    create_summary_stats,
    setup_plotting_context,
    save_plot,
    print_section_header,
    print_dataframe_info
)

__all__ = [
    "get_database_engine",
    "test_connection", 
    "validate_environment",
    "validate_dataframe",
    "setup_notebook_environment",
    "load_data_with_validation",
    "create_summary_stats",
    "setup_plotting_context",
    "save_plot",
    "print_section_header",
    "print_dataframe_info"
]
