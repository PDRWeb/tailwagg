"""
Shared utilities for Jupyter notebooks.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from typing import Optional, Dict, Any
from .database import get_database_engine, test_connection
from .validation import validate_environment
from ..config import PLOT_STYLE, PLOT_PALETTE, FIGURE_SIZE


def setup_notebook_environment(
    suppress_warnings: bool = True,
    set_plotting_style: bool = True,
    validate_db: bool = True
) -> Dict[str, Any]:
    """
    Set up the notebook environment with common configurations.
    
    Parameters:
    -----------
    suppress_warnings : bool
        Whether to suppress warnings (default: True)
    set_plotting_style : bool
        Whether to set plotting style (default: True)
    validate_db : bool
        Whether to validate database connection (default: True)
    
    Returns:
    --------
    dict
        Dictionary with setup information
    """
    setup_info = {
        "warnings_suppressed": False,
        "plotting_style_set": False,
        "database_connected": False,
        "engine": None
    }
    
    # Suppress warnings
    if suppress_warnings:
        warnings.filterwarnings('ignore')
        setup_info["warnings_suppressed"] = True
        print("✅ Warnings suppressed")
    
    # Set plotting style
    if set_plotting_style:
        sns.set_theme(style=PLOT_STYLE, palette=PLOT_PALETTE)
        plt.rcParams["figure.figsize"] = FIGURE_SIZE
        setup_info["plotting_style_set"] = True
        print("✅ Plotting style configured")
    
    # Validate environment and database
    if validate_db:
        try:
            validate_environment()
            engine = get_database_engine()
            if test_connection(engine):
                setup_info["database_connected"] = True
                setup_info["engine"] = engine
                print("✅ Database connection established")
            else:
                print("❌ Database connection failed")
        except Exception as e:
            print(f"❌ Environment validation failed: {e}")
            print("💡 Make sure you have a .env file with database credentials")
    
    return setup_info


def load_data_with_validation(
    query: str,
    engine=None,
    required_columns: Optional[list] = None,
    min_rows: int = 1,
    data_name: str = "Dataset"
) -> pd.DataFrame:
    """
    Load data from database with validation.
    
    Parameters:
    -----------
    query : str
        SQL query to execute
    engine : sqlalchemy.engine.Engine, optional
        Database engine. If None, creates a new one.
    required_columns : list, optional
        List of required columns
    min_rows : int
        Minimum number of rows required
    data_name : str
        Name for error messages
    
    Returns:
    --------
    pd.DataFrame
        Loaded and validated DataFrame
    """
    if engine is None:
        engine = get_database_engine()
    
    try:
        df = pd.read_sql(query, engine)
        print(f"✅ {data_name} loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Validate DataFrame
        from .validation import validate_dataframe
        validate_dataframe(df, required_columns, min_rows, data_name)
        
        return df
    except Exception as e:
        print(f"❌ Failed to load {data_name}: {e}")
        raise


def create_summary_stats(df: pd.DataFrame, title: str = "Dataset Summary") -> None:
    """
    Create a comprehensive summary of the dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to summarize
    title : str
        Title for the summary
    """
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print(f"{'='*60}")
    
    print(f"\n📏 Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    
    print(f"\n💾 Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print(f"\n📅 Date Range:")
    date_cols = df.select_dtypes(include=['datetime64']).columns
    if len(date_cols) > 0:
        for col in date_cols:
            print(f"  {col}: {df[col].min()} to {df[col].max()}")
    else:
        print("  No date columns found")
    
    print(f"\n🔢 Numeric Columns:")
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        print(f"  {', '.join(numeric_cols)}")
    else:
        print("  No numeric columns found")
    
    print(f"\n📝 Categorical Columns:")
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(cat_cols) > 0:
        for col in cat_cols:
            unique_count = df[col].nunique()
            print(f"  {col}: {unique_count} unique values")
    else:
        print("  No categorical columns found")
    
    print(f"\n❓ Missing Values:")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        for col, count in missing[missing > 0].items():
            pct = (count / len(df)) * 100
            print(f"  {col}: {count:,} ({pct:.1f}%)")
    else:
        print("  No missing values found")


def setup_plotting_context(figsize: tuple = (10, 6), style: str = "whitegrid") -> None:
    """
    Set up plotting context for consistent visualizations.
    
    Parameters:
    -----------
    figsize : tuple
        Default figure size (width, height)
    style : str
        Seaborn style to use
    """
    sns.set_theme(style=style, palette=PLOT_PALETTE)
    plt.rcParams["figure.figsize"] = figsize
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 10


def save_plot(fig, filename: str, dpi: int = 300, bbox_inches: str = "tight") -> None:
    """
    Save a plot to the reports/figures directory.
    
    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        Figure to save
    filename : str
        Filename (without extension)
    dpi : int
        Resolution for saving (default: 300)
    bbox_inches : str
        Bounding box for saving (default: "tight")
    """
    import os
    from ..config import FIGURES_DIR
    
    # Ensure directory exists
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    # Save plot
    filepath = os.path.join(FIGURES_DIR, f"{filename}.png")
    fig.savefig(filepath, dpi=dpi, bbox_inches=bbox_inches)
    print(f"✅ Plot saved: {filepath}")


def print_section_header(title: str, char: str = "=", width: int = 60) -> None:
    """
    Print a formatted section header.
    
    Parameters:
    -----------
    title : str
        Section title
    char : str
        Character to use for border (default: "=")
    width : int
        Width of the border (default: 60)
    """
    print(f"\n{char * width}")
    print(f"📊 {title}")
    print(f"{char * width}")


def print_dataframe_info(df: pd.DataFrame, name: str = "DataFrame") -> None:
    """
    Print basic information about a DataFrame.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to analyze
    name : str
        Name for the DataFrame
    """
    print(f"\n📋 {name} Information:")
    print(f"  Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"  Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"  Missing values: {df.isnull().sum().sum()}")
    print(f"  Duplicate rows: {df.duplicated().sum()}")
