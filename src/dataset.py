"""
Dataset utilities for loading and preprocessing data.
"""

import pandas as pd
from sqlalchemy import create_engine
from .config import DATABASE_URL


def load_product_intelligence():
    """Load product intelligence data aggregated from base tables."""
    engine = create_engine(DATABASE_URL)
    query = """
    SELECT
        p.product_id,
        p.sku,
        p.name,
        c.category_name,
        b.brand_name,
        p.is_active,
        COUNT(DISTINCT fs.order_id) as total_orders,
        SUM(fs.quantity) as total_units_sold,
        SUM((fs.unit_price * fs.quantity) - (fs.discount_amount * fs.quantity)) as total_revenue,
        SUM(fs.discount_amount * fs.quantity) as total_discounts,
        SUM(fs.cogs * fs.quantity) as total_cogs,
        SUM((fs.unit_price * fs.quantity) - (fs.discount_amount * fs.quantity)) - SUM(fs.cogs * fs.quantity) as total_profit,
        AVG(fs.unit_price) as avg_unit_price,
        AVG(fs.discount_amount) as avg_discount,
        MIN(fs.order_line_timestamp) as first_sale_date,
        MAX(fs.order_line_timestamp) as last_sale_date
    FROM dim_product p
    LEFT JOIN fact_sales fs ON p.product_id = fs.product_id
    LEFT JOIN dim_category c ON p.category_id = c.category_id
    LEFT JOIN dim_brand b ON p.brand_id = b.brand_id
    GROUP BY p.product_id, p.sku, p.name, c.category_name, b.brand_name, p.is_active
    ORDER BY total_revenue DESC NULLS LAST
    """
    return pd.read_sql(query, engine)


def load_daily_metrics():
    """Load daily product metrics."""
    engine = create_engine(DATABASE_URL)
    query = """
    SELECT
        fs.product_id,
        c.category_name,
        fs.promo_id,
        DATE(fs.order_line_timestamp) AS order_date,
        SUM(fs.quantity) AS total_units_sold,
        SUM((fs.unit_price * fs.quantity) - (fs.discount_amount * fs.quantity)) AS gross_revenue,
        SUM(fs.discount_amount * fs.quantity) AS total_discount,
        SUM(fs.cogs * fs.quantity) AS cogs,
        SUM((fs.unit_price * fs.quantity) - (fs.discount_amount * fs.quantity)) - SUM(fs.cogs * fs.quantity) AS gross_profit
    FROM fact_sales fs
    JOIN dim_product p ON fs.product_id = p.product_id
    JOIN dim_category c ON p.category_id = c.category_id
    GROUP BY 1,2,3,4
    """
    return pd.read_sql(query, engine)


def load_promotions():
    """Load promotion data."""
    engine = create_engine(DATABASE_URL)
    return pd.read_sql_table("dim_promo", engine)
