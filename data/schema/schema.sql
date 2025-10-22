-- Tailwagg Database Schema
-- This file contains all table definitions for the data warehouse

-- Dimensions first (no dependencies)

CREATE TABLE IF NOT EXISTS dim_category (
    category_id TEXT PRIMARY KEY,
    category_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_brand (
    brand_id TEXT PRIMARY KEY,
    brand_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_channel (
    channel_id TEXT PRIMARY KEY,
    channel_name TEXT NOT NULL,
    channel_type TEXT NOT NULL CHECK (channel_type IN ('Paid','Owned','Earned'))
);

CREATE TABLE IF NOT EXISTS dim_location (
    location_id TEXT PRIMARY KEY,
    location_type TEXT NOT NULL CHECK (location_type IN ('online','store')),
    country TEXT NOT NULL,
    region TEXT NOT NULL,
    store_id TEXT
);

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    lifetime_value NUMERIC(12,2) NOT NULL DEFAULT 0,
    loyalty_tier TEXT,
    email_opt_in BOOLEAN NOT NULL DEFAULT FALSE,
    acquisition_channel TEXT
);

CREATE TABLE IF NOT EXISTS dim_promo (
    promo_id TEXT PRIMARY KEY,
    promo_name TEXT NOT NULL,
    promo_type TEXT NOT NULL CHECK (promo_type IN ('discount','bundle','BOGO','coupon')),
    start_date DATE NOT NULL,
    end_date DATE
);

-- Product dimension (depends on category and brand)
CREATE TABLE IF NOT EXISTS dim_product (
    product_id TEXT PRIMARY KEY,
    sku TEXT NOT NULL,
    name TEXT NOT NULL,
    category_id TEXT NOT NULL REFERENCES dim_category(category_id),
    brand_id TEXT NOT NULL REFERENCES dim_brand(brand_id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    attributes JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    discontinued_at TIMESTAMPTZ
);

-- Fact tables (depend on dimensions)

CREATE TABLE IF NOT EXISTS fact_sales (
    order_line_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL REFERENCES dim_product(product_id),
    customer_id TEXT NOT NULL REFERENCES dim_customer(customer_id),
    channel_id TEXT NOT NULL REFERENCES dim_channel(channel_id),
    location_id TEXT NOT NULL REFERENCES dim_location(location_id),
    quantity INT NOT NULL CHECK (quantity >= 0),
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    promo_id TEXT REFERENCES dim_promo(promo_id),
    cogs NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (cogs >= 0),
    order_line_timestamp TIMESTAMPTZ NOT NULL,
    is_returned BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS fact_ad_spend (
    ad_spend_id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    channel_id TEXT NOT NULL REFERENCES dim_channel(channel_id),
    campaign_id TEXT NOT NULL,
    adset_id TEXT,
    creative_id TEXT,
    impressions BIGINT NOT NULL DEFAULT 0 CHECK (impressions >= 0),
    clicks BIGINT NOT NULL DEFAULT 0 CHECK (clicks >= 0),
    conversions BIGINT CHECK (conversions IS NULL OR conversions >= 0),
    spend NUMERIC(14,4) NOT NULL DEFAULT 0 CHECK (spend >= 0),
    revenue_attributed NUMERIC(14,4)
);

CREATE TABLE IF NOT EXISTS fact_email (
    email_event_id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    campaign_id TEXT NOT NULL,
    audience_size BIGINT NOT NULL DEFAULT 0 CHECK (audience_size >= 0),
    sends BIGINT NOT NULL DEFAULT 0 CHECK (sends >= 0),
    opens BIGINT NOT NULL DEFAULT 0 CHECK (opens >= 0),
    clicks BIGINT NOT NULL DEFAULT 0 CHECK (clicks >= 0),
    conversions BIGINT NOT NULL DEFAULT 0 CHECK (conversions >= 0),
    revenue_attributed NUMERIC(14,4) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fact_inventory_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    product_id TEXT NOT NULL REFERENCES dim_product(product_id),
    location_id TEXT NOT NULL REFERENCES dim_location(location_id),
    on_hand INT NOT NULL CHECK (on_hand >= 0),
    available INT NOT NULL CHECK (available >= 0)
);

CREATE TABLE IF NOT EXISTS fact_returns (
    return_id TEXT PRIMARY KEY,
    order_line_id TEXT NOT NULL REFERENCES fact_sales(order_line_id),
    product_id TEXT NOT NULL REFERENCES dim_product(product_id),
    return_reason TEXT,
    return_timestamp TIMESTAMPTZ NOT NULL,
    refund_amount NUMERIC(12,2) NOT NULL CHECK (refund_amount >= 0)
);
