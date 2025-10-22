"""
Visualization utilities for the TailWagg analytics platform.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from .config import PLOT_STYLE, PLOT_PALETTE, FIGURE_SIZE


def setup_plotting():
    """Set up default plotting parameters."""
    sns.set_theme(style=PLOT_STYLE, palette=PLOT_PALETTE)
    plt.rcParams["figure.figsize"] = FIGURE_SIZE


def plot_declining_products(df, title="High-Margin Products Showing Decline"):
    """
    Create a scatter plot of declining high-margin products.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with product data
    title : str
        Plot title
    
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    setup_plotting()
    
    # Filter declining high-margin products
    decliners = df[(df["trend_label"] == "Declining") & (df["net_profit_margin"] > 0.4)]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    sns.scatterplot(
        x="rolling_90d_avg_sales",
        y="gross_profit",
        hue="trend_label",
        data=decliners,
        alpha=0.7,
        s=100,
        ax=ax
    )
    
    # Add product names as labels
    for idx, row in decliners.iterrows():
        ax.annotate(
            row['name'], 
            (row['rolling_90d_avg_sales'], row['gross_profit']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=8,
            alpha=0.8,
            color='black',
            weight='semibold'
        )
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel("90-Day Avg Sales", fontsize=12)
    ax.set_ylabel("Gross Profit", fontsize=12)
    
    plt.tight_layout()
    return fig


def plot_trend_distribution(df, title="Product Performance Trend Classification"):
    """
    Create a count plot of trend labels.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with trend_label column
    title : str
        Plot title
    
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    setup_plotting()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sns.countplot(
        x="trend_label", 
        data=df, 
        order=["Declining", "Plateau", "Growing"],
        ax=ax
    )
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel("Trend Category", fontsize=12)
    ax.set_ylabel("Product Count", fontsize=12)
    
    plt.tight_layout()
    return fig
