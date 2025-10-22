"""
Create processed datasets for Tableau dashboard monitoring.

This script generates 7 CSV files with weekly aggregations and 3-year historical data
to support comprehensive monitoring of TailWagg marketing recommendations.

Usage:
    python -m src.services.create_tableau_datasets
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine
from datetime import datetime
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import DATABASE_URL
from src.utils.database import get_database_engine


def load_base_data():
    """Load interim data and database dimensions."""
    print("Loading base data...")
    
    # Load interim CSVs
    featured_data = pd.read_csv('data/interim/featured_data.csv')
    featured_data['order_date'] = pd.to_datetime(featured_data['order_date'])
    
    calendar_events = pd.read_csv('data/interim/calendar_events.csv')
    calendar_events['date'] = pd.to_datetime(calendar_events['date'])
    
    # Load brand data from raw CSV files (no database connection needed)
    products = pd.read_csv('data/raw/dim_product.csv')
    brands = pd.read_csv('data/raw/dim_brand.csv')
    
    # Merge to get product_id, name, and brand_name
    product_brands = products.merge(brands, on='brand_id', how='left')
    product_brands = product_brands[['product_id', 'name', 'brand_name']]
    product_brands = product_brands.rename(columns={'name': 'product_name'})
    
    print(f"  - Featured data: {len(featured_data):,} rows")
    print(f"  - Calendar events: {len(calendar_events):,} rows")
    print(f"  - Product brands: {len(product_brands):,} products")
    
    return featured_data, calendar_events, product_brands


def aggregate_to_weekly(df, group_cols, agg_dict):
    """
    Aggregate daily data to weekly periods (Monday start).
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe with 'order_date' column
    group_cols : list
        Columns to group by in addition to week
    agg_dict : dict
        Aggregation dictionary for pandas groupby
    
    Returns:
    --------
    pd.DataFrame
        Weekly aggregated dataframe
    """
    df = df.copy()
    df['week_start_date'] = df['order_date'].dt.to_period('W-MON').dt.start_time
    
    # Group by week and other columns
    result = df.groupby(['week_start_date'] + group_cols).agg(agg_dict).reset_index()
    
    # Add week metadata
    result['week_end_date'] = result['week_start_date'] + pd.Timedelta(days=6)
    result['year'] = result['week_start_date'].dt.year
    result['week_number'] = result['week_start_date'].dt.isocalendar().week
    
    return result


def create_weekly_product_performance(featured_data, calendar_events, product_brands):
    """Generate weekly_product_performance.csv"""
    print("\n1. Creating weekly_product_performance.csv...")
    
    # Merge calendar events with featured data
    df = featured_data.copy()
    df = df.merge(
        calendar_events[['date', 'event_name', 'event_category', 'seasonal_event_flag']],
        left_on='order_date',
        right_on='date',
        how='left'
    )
    
    # Add brand information
    df = df.merge(product_brands, on='product_id', how='left')
    
    # Create weekly aggregations
    agg_dict = {
        'total_units_sold': 'sum',
        'gross_revenue': 'sum',
        'gross_profit': 'sum',
        'rolling_30d_avg_sales': 'mean',
        'rolling_90d_avg_sales': 'mean',
        'trend_ratio': 'mean',
        'net_profit_margin': 'mean',
        'seasonal_event_flag': 'max',  # True if any day in week has event
        'event_name': lambda x: ', '.join(x.dropna().unique()) if x.notna().any() else '',
        'promo_id': lambda x: x.notna().sum()  # Count of promo days
    }
    
    weekly = aggregate_to_weekly(
        df,
        group_cols=['product_id', 'category_name', 'brand_name'],
        agg_dict=agg_dict
    )
    
    # Calculate derived fields
    weekly['has_promotion'] = weekly['promo_id'] > 0
    weekly['promo_count'] = weekly['promo_id']
    weekly = weekly.rename(columns={'event_name': 'event_names'})
    
    # Recalculate trend labels based on weekly averages
    weekly['trend_label'] = np.where(
        weekly['trend_ratio'] < 0.95, 'Declining',
        np.where(weekly['trend_ratio'] < 1.05, 'Plateau', 'Growing')
    )
    
    # Select and order columns
    columns = [
        'week_start_date', 'week_end_date', 'year', 'week_number',
        'product_id', 'category_name', 'brand_name',
        'total_units_sold', 'gross_revenue', 'gross_profit', 'net_profit_margin',
        'rolling_30d_avg_sales', 'rolling_90d_avg_sales', 'trend_ratio', 'trend_label',
        'has_promotion', 'promo_count',
        'seasonal_event_flag', 'event_names'
    ]
    
    result = weekly[columns].sort_values(['week_start_date', 'product_id'])
    
    output_path = 'data/processed/weekly_product_performance.csv'
    result.to_csv(output_path, index=False)
    print(f"  ✓ Saved {len(result):,} rows to {output_path}")
    
    return result


def create_reactivation_tracker(weekly_product):
    """Generate reactivation_tracker.csv"""
    print("\n2. Creating reactivation_tracker.csv...")
    
    df = weekly_product.copy()
    
    # Filter for high-margin products (>40%)
    df['is_reactivation_target'] = (df['net_profit_margin'] > 0.40) & (df['trend_label'] == 'Declining')
    
    # Calculate weeks declining using cumulative count reset
    df = df.sort_values(['product_id', 'week_start_date'])
    df['is_declining'] = (df['trend_label'] == 'Declining').astype(int)
    df['declining_group'] = (df['is_declining'] != df.groupby('product_id')['is_declining'].shift()).cumsum()
    df['weeks_declining'] = df.groupby(['product_id', 'declining_group']).cumcount() + 1
    df.loc[df['trend_label'] != 'Declining', 'weeks_declining'] = 0
    
    # Calculate baseline (90 days = ~13 weeks ago)
    df = df.sort_values(['product_id', 'week_start_date'])
    df['baseline_90d_avg'] = df.groupby('product_id')['rolling_90d_avg_sales'].shift(13)
    
    # Calculate current weekly sales and change vs baseline
    df['current_weekly_sales'] = df['total_units_sold']
    df['vs_baseline_pct_change'] = (
        (df['current_weekly_sales'] - df['baseline_90d_avg']) / 
        (df['baseline_90d_avg'] + 1e-9) * 100
    )
    
    # Calculate profit at risk (difference in profit if sales continue declining)
    df['total_profit_at_risk'] = np.where(
        df['is_reactivation_target'],
        np.maximum(0, (df['baseline_90d_avg'] - df['current_weekly_sales']) * 
                   df['gross_profit'] / (df['total_units_sold'] + 1e-9)),
        0
    )
    
    # Select columns
    columns = [
        'week_start_date', 'product_id', 'category_name',
        'net_profit_margin', 'trend_label', 'is_reactivation_target',
        'weeks_declining', 'baseline_90d_avg',
        'current_weekly_sales', 'vs_baseline_pct_change',
        'total_profit_at_risk'
    ]
    
    result = df[columns].sort_values(['week_start_date', 'product_id'])
    
    output_path = 'data/processed/reactivation_tracker.csv'
    result.to_csv(output_path, index=False)
    print(f"  ✓ Saved {len(result):,} rows to {output_path}")
    
    return result


def create_seasonal_event_performance(featured_data, calendar_events):
    """Generate seasonal_event_performance.csv"""
    print("\n3. Creating seasonal_event_performance.csv...")
    
    # Merge calendar events
    df = featured_data.copy()
    df = df.merge(
        calendar_events[['date', 'event_name', 'event_category', 'seasonal_event_flag']],
        left_on='order_date',
        right_on='date',
        how='left'
    )
    
    # Filter to only seasonal event periods
    df_events = df[df['seasonal_event_flag'] == True].copy()
    
    # Calculate baseline (non-event periods)
    df_baseline = df[df['seasonal_event_flag'] == False].groupby('category_name').agg({
        'gross_revenue': 'mean',
        'gross_profit': 'mean'
    }).add_suffix('_baseline')
    
    # Weekly aggregation for events
    df_events['week_start_date'] = df_events['order_date'].dt.to_period('W-MON').dt.start_time
    
    # Aggregate by week and event
    weekly_events = df_events.groupby(['week_start_date', 'event_name', 'event_category']).agg({
        'order_date': 'count',  # transaction count
        'gross_revenue': 'sum',
        'gross_profit': 'sum',
        'category_name': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]  # top category
    }).reset_index()
    
    weekly_events = weekly_events.rename(columns={
        'order_date': 'total_transactions',
        'category_name': 'top_performing_category'
    })
    
    # Calculate average order value
    weekly_events['avg_order_value'] = weekly_events['gross_revenue'] / weekly_events['total_transactions']
    
    # Calculate category breakdown separately
    category_breakdown = df_events.groupby(['week_start_date', 'event_name', 'category_name']).agg({
        'gross_revenue': 'sum',
        'gross_profit': 'sum'
    }).reset_index()
    
    # Join baseline for lift calculations
    category_breakdown = category_breakdown.merge(
        df_baseline,
        left_on='category_name',
        right_index=True,
        how='left'
    )
    
    # Calculate lifts at category level
    category_breakdown['revenue_lift_pct'] = (
        (category_breakdown['gross_revenue'] - category_breakdown['gross_revenue_baseline']) /
        (category_breakdown['gross_revenue_baseline'] + 1e-9) * 100
    )
    category_breakdown['profit_lift_pct'] = (
        (category_breakdown['gross_profit'] - category_breakdown['gross_profit_baseline']) /
        (category_breakdown['gross_profit_baseline'] + 1e-9) * 100
    )
    
    # Aggregate lifts back to weekly event level
    lift_summary = category_breakdown.groupby(['week_start_date', 'event_name']).agg({
        'revenue_lift_pct': 'mean',
        'profit_lift_pct': 'mean'
    }).reset_index()
    
    # Merge lifts with main event data
    result = weekly_events.merge(
        lift_summary,
        on=['week_start_date', 'event_name'],
        how='left'
    )
    
    result = result.rename(columns={
        'revenue_lift_pct': 'vs_baseline_revenue_lift_pct',
        'profit_lift_pct': 'vs_baseline_profit_lift_pct'
    })
    
    # Add category breakdown as JSON-like string
    category_json = category_breakdown.groupby(['week_start_date', 'event_name']).apply(
        lambda x: '; '.join([f"{row['category_name']}: ${row['gross_revenue']:.2f}" 
                            for _, row in x.iterrows()])
    ).reset_index(name='category_breakdown')
    
    result = result.merge(category_json, on=['week_start_date', 'event_name'], how='left')
    
    # Select and order columns
    columns = [
        'week_start_date', 'event_name', 'event_category',
        'total_transactions', 'gross_revenue', 'gross_profit', 'avg_order_value',
        'category_breakdown',
        'vs_baseline_revenue_lift_pct', 'vs_baseline_profit_lift_pct',
        'top_performing_category'
    ]
    
    result = result[columns].sort_values(['week_start_date', 'event_name'])
    
    output_path = 'data/processed/seasonal_event_performance.csv'
    result.to_csv(output_path, index=False)
    print(f"  ✓ Saved {len(result):,} rows to {output_path}")
    
    return result


def create_category_performance_weekly(featured_data, calendar_events):
    """Generate category_performance_weekly.csv"""
    print("\n4. Creating category_performance_weekly.csv...")
    
    # Merge calendar events
    df = featured_data.copy()
    df = df.merge(
        calendar_events[['date', 'seasonal_event_flag']],
        left_on='order_date',
        right_on='date',
        how='left'
    )
    
    df['week_start_date'] = df['order_date'].dt.to_period('W-MON').dt.start_time
    
    # Aggregate by week and category
    weekly = df.groupby(['week_start_date', 'category_name']).agg({
        'gross_revenue': 'sum',
        'gross_profit': 'sum',
        'total_units_sold': 'sum',
        'product_id': 'nunique',
        'promo_id': lambda x: x.notna().sum(),
        'seasonal_event_flag': 'max'
    }).reset_index()
    
    weekly = weekly.rename(columns={
        'gross_revenue': 'total_revenue',
        'gross_profit': 'total_profit',
        'total_units_sold': 'total_units',
        'product_id': 'unique_products_sold',
        'promo_id': 'promo_transaction_count'
    })
    
    # Calculate average margin
    weekly['avg_margin'] = (weekly['total_profit'] / (weekly['total_revenue'] + 1e-9)) * 100
    
    # Count products by trend (from weekly product performance)
    # Need to aggregate trend counts per week/category
    df['trend_declining'] = (df['trend_label'] == 'Declining').astype(int)
    df['trend_growing'] = (df['trend_label'] == 'Growing').astype(int)
    df['trend_plateau'] = (df['trend_label'] == 'Plateau').astype(int)
    
    trend_counts = df.groupby(['week_start_date', 'category_name']).agg({
        'trend_declining': 'sum',
        'trend_growing': 'sum',
        'trend_plateau': 'sum'
    }).reset_index()
    
    trend_counts = trend_counts.rename(columns={
        'trend_declining': 'products_declining',
        'trend_growing': 'products_growing',
        'trend_plateau': 'products_plateau'
    })
    
    # Merge trend counts
    weekly = weekly.merge(trend_counts, on=['week_start_date', 'category_name'], how='left')
    
    # Calculate total transactions for promo penetration
    total_transactions = df.groupby(['week_start_date', 'category_name']).size().reset_index(name='total_transactions')
    weekly = weekly.merge(total_transactions, on=['week_start_date', 'category_name'], how='left')
    
    # Calculate promo penetration
    weekly['promo_penetration_pct'] = (
        weekly['promo_transaction_count'] / (weekly['total_transactions'] + 1e-9) * 100
    )
    
    # Select and order columns
    columns = [
        'week_start_date', 'category_name',
        'total_revenue', 'total_profit', 'total_units', 'unique_products_sold',
        'avg_margin', 'products_declining', 'products_growing', 'products_plateau',
        'promo_penetration_pct', 'seasonal_event_flag'
    ]
    
    result = weekly[columns].sort_values(['week_start_date', 'category_name'])
    
    output_path = 'data/processed/category_performance_weekly.csv'
    result.to_csv(output_path, index=False)
    print(f"  ✓ Saved {len(result):,} rows to {output_path}")
    
    return result


def create_promotional_effectiveness(featured_data):
    """Generate promotional_effectiveness.csv"""
    print("\n5. Creating promotional_effectiveness.csv...")
    
    df = featured_data.copy()
    df['week_start_date'] = df['order_date'].dt.to_period('W-MON').dt.start_time
    df['has_promotion'] = df['promo_id'].notna()
    
    # Aggregate by week, category, and promo status
    weekly = df.groupby(['week_start_date', 'category_name', 'has_promotion']).agg({
        'order_date': 'count',  # transaction count
        'gross_revenue': ['sum', 'mean'],
        'total_units_sold': 'mean',
        'total_discount': 'sum',
        'gross_profit': 'sum'
    }).reset_index()
    
    # Flatten multi-level columns
    weekly.columns = [
        'week_start_date', 'category_name', 'has_promotion',
        'transaction_count', 'total_revenue', 'avg_revenue_per_transaction',
        'avg_units_per_transaction', 'total_discount_amount', 'gross_profit'
    ]
    
    # Calculate discount percentage
    weekly['discount_pct_of_revenue'] = (
        weekly['total_discount_amount'] / (weekly['total_revenue'] + 1e-9) * 100
    )
    
    # Calculate net margin
    weekly['net_margin'] = (
        weekly['gross_profit'] / (weekly['total_revenue'] + 1e-9) * 100
    )
    
    # Calculate uplift vs non-promo (per week/category)
    # Pivot to get promo vs non-promo side by side
    pivot_revenue = weekly.pivot_table(
        index=['week_start_date', 'category_name'],
        columns='has_promotion',
        values='avg_revenue_per_transaction',
        aggfunc='first'
    ).reset_index()
    
    pivot_revenue.columns = ['week_start_date', 'category_name', 'revenue_no_promo', 'revenue_with_promo']
    pivot_revenue['uplift_vs_non_promo'] = (
        (pivot_revenue['revenue_with_promo'] - pivot_revenue['revenue_no_promo']) /
        (pivot_revenue['revenue_no_promo'] + 1e-9) * 100
    )
    
    # Merge uplift back
    result = weekly.merge(
        pivot_revenue[['week_start_date', 'category_name', 'uplift_vs_non_promo']],
        on=['week_start_date', 'category_name'],
        how='left'
    )
    
    # Select and order columns
    columns = [
        'week_start_date', 'category_name', 'has_promotion',
        'transaction_count', 'avg_revenue_per_transaction', 'avg_units_per_transaction',
        'total_discount_amount', 'discount_pct_of_revenue',
        'gross_profit', 'net_margin',
        'uplift_vs_non_promo'
    ]
    
    result = result[columns].sort_values(['week_start_date', 'category_name', 'has_promotion'])
    
    output_path = 'data/processed/promotional_effectiveness.csv'
    result.to_csv(output_path, index=False)
    print(f"  ✓ Saved {len(result):,} rows to {output_path}")
    
    return result


def create_kpi_dashboard(featured_data, calendar_events, reactivation_tracker):
    """Generate kpi_dashboard.csv"""
    print("\n6. Creating kpi_dashboard.csv...")
    
    # Merge calendar events
    df = featured_data.copy()
    df = df.merge(
        calendar_events[['date', 'seasonal_event_flag']],
        left_on='order_date',
        right_on='date',
        how='left'
    )
    
    df['week_start_date'] = df['order_date'].dt.to_period('W-MON').dt.start_time
    
    # Weekly revenue and metrics
    weekly_metrics = df.groupby('week_start_date').agg({
        'gross_revenue': 'sum',
        'gross_profit': 'sum',
        'total_discount': 'sum',
        'seasonal_event_flag': 'max'
    }).reset_index()
    
    weekly_metrics = weekly_metrics.rename(columns={
        'gross_revenue': 'weekly_revenue',
        'total_discount': 'total_discount_spend',
        'seasonal_event_flag': 'seasonal_event_active'
    })
    
    # Calculate gross profit margin
    weekly_metrics['gross_profit_margin_pct'] = (
        weekly_metrics['gross_profit'] / (weekly_metrics['weekly_revenue'] + 1e-9) * 100
    )
    
    # Calculate promotional ROI
    weekly_metrics['promotional_roi'] = (
        weekly_metrics['weekly_revenue'] / (weekly_metrics['total_discount_spend'] + 1e-9)
    )
    
    # Calculate baseline (first 13 weeks average)
    baseline_revenue = weekly_metrics.head(13)['weekly_revenue'].mean()
    baseline_aov = df[df['order_date'] < df['order_date'].min() + pd.Timedelta(days=91)].groupby('order_date')['gross_revenue'].mean().mean()
    
    # Calculate average order value (AOV) per week
    aov_weekly = df.groupby('week_start_date')['gross_revenue'].mean().reset_index()
    aov_weekly = aov_weekly.rename(columns={'gross_revenue': 'avg_order_value'})
    
    weekly_metrics = weekly_metrics.merge(aov_weekly, on='week_start_date', how='left')
    
    # Calculate vs baseline
    weekly_metrics['vs_baseline_revenue_lift_pct'] = (
        (weekly_metrics['weekly_revenue'] - baseline_revenue) / baseline_revenue * 100
    )
    weekly_metrics['vs_baseline_aov_pct'] = (
        (weekly_metrics['avg_order_value'] - baseline_aov) / baseline_aov * 100
    )
    
    # Product counts from reactivation tracker
    product_counts = reactivation_tracker.groupby('week_start_date').agg({
        'trend_label': lambda x: (x == 'Declining').sum(),
        'is_reactivation_target': 'sum'
    }).reset_index()
    
    product_counts = product_counts.rename(columns={
        'trend_label': 'declining_product_count',
        'is_reactivation_target': 'high_margin_declining_count'
    })
    
    # Merge product counts
    weekly_metrics = weekly_metrics.merge(product_counts, on='week_start_date', how='left')
    
    # Calculate reactivation rate
    # Products that were declining in previous week but are now growing/plateau
    reactivation_tracker_sorted = reactivation_tracker.sort_values(['product_id', 'week_start_date'])
    reactivation_tracker_sorted['prev_trend'] = reactivation_tracker_sorted.groupby('product_id')['trend_label'].shift(1)
    
    reactivation_tracker_sorted['reactivated'] = (
        (reactivation_tracker_sorted['prev_trend'] == 'Declining') &
        (reactivation_tracker_sorted['trend_label'].isin(['Growing', 'Plateau']))
    ).astype(int)
    
    reactivation_weekly = reactivation_tracker_sorted.groupby('week_start_date').agg({
        'reactivated': 'sum',
        'product_id': lambda x: ((reactivation_tracker_sorted.loc[x.index, 'prev_trend'] == 'Declining')).sum()
    }).reset_index()
    
    reactivation_weekly.columns = ['week_start_date', 'products_reactivated', 'products_previously_declining']
    reactivation_weekly['reactivation_rate'] = (
        reactivation_weekly['products_reactivated'] / 
        (reactivation_weekly['products_previously_declining'] + 1e-9) * 100
    )
    
    # Merge reactivation rate
    weekly_metrics = weekly_metrics.merge(
        reactivation_weekly[['week_start_date', 'reactivation_rate']],
        on='week_start_date',
        how='left'
    )
    
    # Fill missing values
    weekly_metrics['reactivation_rate'] = weekly_metrics['reactivation_rate'].fillna(0)
    weekly_metrics['declining_product_count'] = weekly_metrics['declining_product_count'].fillna(0).astype(int)
    weekly_metrics['high_margin_declining_count'] = weekly_metrics['high_margin_declining_count'].fillna(0).astype(int)
    
    # Select and order columns
    columns = [
        'week_start_date',
        'reactivation_rate',
        'weekly_revenue', 'vs_baseline_revenue_lift_pct',
        'promotional_roi',
        'avg_order_value', 'vs_baseline_aov_pct',
        'gross_profit_margin_pct',
        'declining_product_count', 'high_margin_declining_count',
        'seasonal_event_active'
    ]
    
    result = weekly_metrics[columns].sort_values('week_start_date')
    
    output_path = 'data/processed/kpi_dashboard.csv'
    result.to_csv(output_path, index=False)
    print(f"  ✓ Saved {len(result):,} rows to {output_path}")
    
    return result


def create_campaign_timeline_reference():
    """Generate campaign_timeline_reference.csv (static reference table)"""
    print("\n7. Creating campaign_timeline_reference.csv...")
    
    campaigns = [
        {
            'campaign_phase': 'Early Bird Holiday',
            'start_date': '2025-10-20',
            'end_date': '2025-11-10',
            'duration_days': 22,
            'target_audience': 'Loyalty members and high-value customers',
            'target_products': 'High-margin declining Accessories, Wellness',
            'channels': 'Email/SMS',
            'messaging_theme': 'Be the first to save on holiday must-haves',
            'recommended_categories': 'Accessories, Wellness',
            'discount_range': '15-20%'
        },
        {
            'campaign_phase': 'Pre-Black Friday',
            'start_date': '2025-11-11',
            'end_date': '2025-11-27',
            'duration_days': 17,
            'target_audience': 'All customers',
            'target_products': 'Grooming, Toys bundles',
            'channels': 'Paid Social (Instagram/TikTok)',
            'messaging_theme': 'Get ready for the biggest savings',
            'recommended_categories': 'Grooming, Toys',
            'discount_range': '10-15%'
        },
        {
            'campaign_phase': 'Black Friday/Cyber Monday',
            'start_date': '2025-11-28',
            'end_date': '2025-12-02',
            'duration_days': 5,
            'target_audience': 'All customers - omnichannel',
            'target_products': 'All reactivation targets + top performers',
            'channels': 'Social, Email, Paid Search, Amazon',
            'messaging_theme': 'Biggest savings of the year + Limited stock urgency',
            'recommended_categories': 'All categories',
            'discount_range': '20-30%'
        },
        {
            'campaign_phase': 'Holiday Gifting',
            'start_date': '2025-12-03',
            'end_date': '2025-12-20',
            'duration_days': 18,
            'target_audience': 'Gift buyers, first-time customers',
            'target_products': 'Toys, Treats bundles, Accessories',
            'channels': 'Instagram/TikTok Ads, Paid Search',
            'messaging_theme': 'Perfect presents for your pup + Free gift wrapping',
            'recommended_categories': 'Toys, Treats, Accessories',
            'discount_range': '15-25%'
        },
        {
            'campaign_phase': 'Last Minute Rush',
            'start_date': '2025-12-21',
            'end_date': '2025-12-24',
            'duration_days': 4,
            'target_audience': 'Last-minute shoppers',
            'target_products': 'Fast-ship, digital products',
            'channels': 'Search + Email urgency',
            'messaging_theme': 'Still time for pup gifts! Express shipping available',
            'recommended_categories': 'Toys, Treats',
            'discount_range': '10-20%'
        },
        {
            'campaign_phase': 'New Year Wellness',
            'start_date': '2025-12-26',
            'end_date': '2026-01-15',
            'duration_days': 21,
            'target_audience': 'Health-conscious pet parents, subscription customers',
            'target_products': 'Wellness category (supplements, vitamins)',
            'channels': 'Paid Search, Email',
            'messaging_theme': 'New year, healthier dog + Subscription upgrades',
            'recommended_categories': 'Wellness',
            'discount_range': '15-20%'
        }
    ]
    
    result = pd.DataFrame(campaigns)
    
    output_path = 'data/processed/campaign_timeline_reference.csv'
    result.to_csv(output_path, index=False)
    print(f"  ✓ Saved {len(result):,} rows to {output_path}")
    
    return result


def main():
    """Main execution function"""
    print("="*70)
    print("TailWagg Tableau Dashboard Dataset Generator")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Ensure output directory exists
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    
    # Load base data
    featured_data, calendar_events, product_brands = load_base_data()
    
    # Generate all datasets
    weekly_product = create_weekly_product_performance(featured_data, calendar_events, product_brands)
    reactivation_tracker = create_reactivation_tracker(weekly_product)
    seasonal_events = create_seasonal_event_performance(featured_data, calendar_events)
    category_weekly = create_category_performance_weekly(featured_data, calendar_events)
    promo_effectiveness = create_promotional_effectiveness(featured_data)
    kpi_dashboard = create_kpi_dashboard(featured_data, calendar_events, reactivation_tracker)
    campaign_timeline = create_campaign_timeline_reference()
    
    # Create summary report
    print("\n" + "="*70)
    print("SUMMARY REPORT")
    print("="*70)
    print(f"\nDate range: {featured_data['order_date'].min().date()} to {featured_data['order_date'].max().date()}")
    print(f"Total weeks: {weekly_product['week_start_date'].nunique()}")
    print(f"Total products: {featured_data['product_id'].nunique()}")
    print(f"Total categories: {featured_data['category_name'].nunique()}")
    
    print("\n✅ All 7 datasets generated successfully!")
    print("\nGenerated files:")
    print("  1. weekly_product_performance.csv")
    print("  2. reactivation_tracker.csv")
    print("  3. seasonal_event_performance.csv")
    print("  4. category_performance_weekly.csv")
    print("  5. promotional_effectiveness.csv")
    print("  6. kpi_dashboard.csv")
    print("  7. campaign_timeline_reference.csv")
    
    print(f"\n✓ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)


if __name__ == "__main__":
    main()

