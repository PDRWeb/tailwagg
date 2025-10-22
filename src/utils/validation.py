"""
Validation utilities for the TailWagg analytics platform.
"""

import os
import pandas as pd
from typing import List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def validate_environment() -> None:
    """
    Validate that all required environment variables are set.
    
    Raises:
    -------
    ValueError
        If any required environment variables are missing
    """
    required_vars = [
        "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}. "
            f"Please check your .env file or set these variables."
        )


def validate_dataframe(df: pd.DataFrame, 
                      required_columns: Optional[List[str]] = None,
                      min_rows: int = 1,
                      name: str = "DataFrame") -> None:
    """
    Validate a pandas DataFrame.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to validate
    required_columns : list of str, optional
        List of required column names
    min_rows : int
        Minimum number of rows required (default: 1)
    name : str
        Name of the DataFrame for error messages (default: "DataFrame")
    
    Raises:
    -------
    ValueError
        If DataFrame validation fails
    """
    if df is None:
        raise ValueError(f"{name} is None")
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"{name} is not a pandas DataFrame")
    
    if len(df) < min_rows:
        raise ValueError(f"{name} has {len(df)} rows, but minimum {min_rows} required")
    
    if required_columns:
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"{name} is missing required columns: {', '.join(missing_cols)}"
            )


def validate_notebook_environment() -> None:
    """
    Validate that the notebook environment is properly set up.
    
    Raises:
    -------
    ValueError
        If environment validation fails
    """
    try:
        validate_environment()
        print("✅ Environment validation passed")
    except ValueError as e:
        print(f"❌ Environment validation failed: {e}")
        print("\nTo fix this:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your database credentials")
        print("3. Restart your notebook kernel")
        raise


def check_database_tables(engine, required_tables: List[str]) -> None:
    """
    Check if required database tables exist.
    
    Parameters:
    -----------
    engine : sqlalchemy.engine.Engine
        Database engine
    required_tables : list of str
        List of required table names
    
    Raises:
    -------
    ValueError
        If any required tables are missing
    """
    from sqlalchemy import text
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        existing_tables = {row[0] for row in result}
    
    missing_tables = set(required_tables) - existing_tables
    if missing_tables:
        raise ValueError(
            f"Missing required database tables: {', '.join(missing_tables)}. "
            f"Please run the schema creation script first."
        )
