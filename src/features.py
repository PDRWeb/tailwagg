"""
Feature engineering utilities for the TailWagg analytics platform.
"""

import pandas as pd
import numpy as np


def calculate_rolling_averages(df, group_col='product_id', date_col='order_date', 
                             value_col='total_units_sold', windows=[30, 90]):
    """
    Calculate rolling averages for specified windows.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    group_col : str
        Column to group by (default: 'product_id')
    date_col : str
        Date column name (default: 'order_date')
    value_col : str
        Value column to calculate rolling average (default: 'total_units_sold')
    windows : list
        List of window sizes in days (default: [30, 90])
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with rolling average columns added
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values([group_col, date_col])
    
    for window in windows:
        col_name = f"rolling_{window}d_avg_sales"
        df[col_name] = (
            df.groupby(group_col)[value_col]
            .rolling(window=window, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )
    
    return df


def calculate_trend_labels(df, short_col='rolling_30d_avg_sales', 
                          long_col='rolling_90d_avg_sales'):
    """
    Calculate trend labels based on rolling average ratios.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    short_col : str
        Short-term rolling average column
    long_col : str
        Long-term rolling average column
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with trend_label column added
    """
    df = df.copy()
    
    # Calculate trend ratio
    df["trend_ratio"] = df[short_col] / (df[long_col] + 1e-9)
    
    # Assign trend labels
    df["trend_label"] = np.where(
        df["trend_ratio"] < 0.95, "Declining",
        np.where(df["trend_ratio"] < 1.05, "Plateau", "Growing")
    )
    
    return df


def calculate_net_profit_margin(df, profit_col='gross_profit', revenue_col='gross_revenue'):
    """
    Calculate net profit margin.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    profit_col : str
        Profit column name
    revenue_col : str
        Revenue column name
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with net_profit_margin column added
    """
    df = df.copy()
    df["net_profit_margin"] = df[profit_col] / (df[revenue_col] + 1e-9)
    return df
