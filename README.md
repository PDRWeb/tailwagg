# TailWagg Analytics Platform

A comprehensive analytics platform for pet retail business intelligence, featuring sales forecasting, promotional analysis, and product performance metrics.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## Table of Contents

- [Quick Start](#quick-start)
- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Processed Data Guide](#processed-data-guide)
- [Project Structure](#project-structure)
- [Notebooks Guide](#notebooks-guide)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

## Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/tailwagg.git
cd tailwagg

# 2. Set up environment
cp .env.example .env
# Edit .env with your database credentials

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start database
docker compose up -d

# 5. Create schema and generate data
python -m src.services.create_schema
python -m src.services.generate_data

# 6. Start Jupyter
jupyter notebook
```

## Project Overview

**TailWagg** is a data-driven analytics platform designed for pet retail businesses to optimize their marketing strategies and product performance. The platform analyzes three years of sales and marketing data to identify:

- **High-margin products** with growth potential
- **Promotional opportunities** for declining products
- **Seasonal trends** and holiday performance patterns
- **Customer behavior** insights across different channels

### Key Features

- **Product Intelligence**: Comprehensive product performance analysis
- **Seasonal Analysis**: Holiday and event-driven sales insights
- **Interactive Dashboards**: Jupyter notebooks with rich visualizations
- **Data Pipeline**: Automated data generation and processing
- **Modular Design**: Reusable components for different use cases

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Docker & Docker Compose** ([Download](https://www.docker.com/get-started))
- **Git** ([Download](https://git-scm.com/downloads))

### System Requirements

- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **OS**: Windows 10+, macOS 10.14+, or Linux

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/tailwagg.git
cd tailwagg

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### 1. Environment Setup

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env  # or use your preferred editor
```

### 2. Database Configuration

Edit `.env` file with your PostgreSQL credentials:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tailwagg
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Data Generation Settings
RANDOM_SEED=42
```

### 3. Start Database

```bash
# Start PostgreSQL with Docker
docker compose up -d

# Verify database is running
docker compose ps
```

## Usage

### 1. Initialize Database

```bash
# Create database schema
python -m src.services.create_schema

# Generate sample data (3 years of data)
python -m src.services.generate_data
```

### 2. Run Analysis

```bash
# Start Jupyter Notebook
jupyter notebook

# Or start JupyterLab
jupyter lab
```

### 3. Explore Notebooks

1. **`1.0-pdr-initial-data-exploration.ipynb`** - Initial data exploration and basic analysis
2. **`2.0-pdr-calendar-events-analysis.ipynb`** - Holiday and seasonal event analysis
3. **`3.0-pdr-product-performance-analysis.ipynb`** - Product-specific performance analysis
4. **`4.0-pdr-feature-engineering.ipynb`** - Feature engineering and data preprocessing
5. **`5.0-pdr-final-insights-visualization.ipynb`** - Final insights and business recommendations

### 4. Use Python API

```python
from src.dataset import load_product_intelligence, load_daily_metrics
from src.plots import plot_declining_products, plot_trend_distribution
from src.utils import get_database_engine

# Load data
df = load_product_intelligence()

# Create visualizations
fig = plot_declining_products(df)
```

### 5. Generate Tableau Dashboard Datasets

```bash
# Generate processed datasets for Tableau dashboard
python3 src/services/create_tableau_datasets.py
```

This generates 7 CSV files in `data/processed/` with weekly aggregations and 3-year historical data:

1. **weekly_product_performance.csv** (65,856 rows) - Core product metrics with trend classifications
2. **reactivation_tracker.csv** (65,856 rows) - Declining high-margin product monitoring
3. **seasonal_event_performance.csv** (51 rows) - Event vs baseline performance comparisons
4. **category_performance_weekly.csv** (790 rows) - Category-level portfolio health metrics
5. **promotional_effectiveness.csv** (1,580 rows) - Promo vs non-promo comparisons
6. **kpi_dashboard.csv** (158 rows) - High-level strategic KPIs
7. **campaign_timeline_reference.csv** (6 rows) - Recommended campaign phases

See [Processed Data Guide](#processed-data-guide) below for detailed field descriptions.

## Processed Data Guide

The `data/processed/` folder contains weekly-aggregated datasets optimized for Tableau dashboard monitoring. All datasets cover the full 3-year period (Oct 2022 - Oct 2025) with ~158 weeks of data.

### Dataset Descriptions

#### 1. weekly_product_performance.csv

**Purpose**: Core dataset tracking all 457 products with trend classifications and key metrics.

**Key Fields**:

- **Time**: `week_start_date`, `week_end_date`, `year`, `week_number`
- **Identifiers**: `product_id`, `category_name`, `brand_name`
- **Performance**: `total_units_sold`, `gross_revenue`, `gross_profit`, `net_profit_margin`
- **Trends**: `rolling_30d_avg_sales`, `rolling_90d_avg_sales`, `trend_ratio`, `trend_label` (Declining/Plateau/Growing)
- **Promotions**: `has_promotion` (boolean), `promo_count`
- **Events**: `seasonal_event_flag`, `event_names`

**Use Cases**:

- Track individual product performance over time
- Filter by trend_label to identify declining/growing products
- Analyze promotional effectiveness by product
- Monitor seasonal event impact

#### 2. reactivation_tracker.csv

**Purpose**: Monitor declining high-margin products (>40% margin) - Priority reactivation targets.

**Key Fields**:

- `is_reactivation_target` (boolean) - High-margin (>40%) declining products
- `weeks_declining` - Consecutive weeks in decline
- `baseline_90d_avg` - Sales baseline from 13 weeks ago
- `current_weekly_sales` - Current week sales volume
- `vs_baseline_pct_change` - Percentage change vs baseline
- `total_profit_at_risk` - Potential lost profit from decline

**Use Cases**:

- Identify priority reactivation targets
- Track reactivation campaign effectiveness
- Monitor profit at risk from declining products
- Measure weeks in decline for urgency prioritization

#### 3. seasonal_event_performance.csv

**Purpose**: Track performance during seasonal events vs non-event baseline periods.

**Key Fields**:

- `event_name`, `event_category` (Federal Holiday, Pet Industry Events, Major Retail Events)
- `total_transactions`, `gross_revenue`, `gross_profit`, `avg_order_value`
- `category_breakdown` - Revenue by category during event
- `vs_baseline_revenue_lift_pct` - Revenue lift vs non-event baseline
- `vs_baseline_profit_lift_pct` - Profit lift vs non-event baseline
- `top_performing_category` - Best category during event

**Use Cases**:

- Compare event vs baseline performance
- Identify highest-performing seasonal events
- Plan marketing calendar based on historical event ROI
- Optimize category focus by event type

#### 4. category_performance_weekly.csv

**Purpose**: Weekly category-level aggregations for portfolio health monitoring.

**Key Fields**:

- `total_revenue`, `total_profit`, `total_units`, `unique_products_sold`
- `avg_margin` - Average profit margin for category
- `products_declining`, `products_growing`, `products_plateau` - Product health counts
- `promo_penetration_pct` - Percentage of sales with promotions
- `seasonal_event_flag` - Whether week includes seasonal events

**Use Cases**:

- Monitor category portfolio health
- Track margin trends by category
- Compare promotional usage across categories
- Identify categories needing intervention

#### 5. promotional_effectiveness.csv

**Purpose**: Compare promotional vs non-promotional performance by category.

**Key Fields**:

- `has_promotion` (boolean) - Promotion status
- `transaction_count`, `avg_revenue_per_transaction`, `avg_units_per_transaction`
- `total_discount_amount`, `discount_pct_of_revenue`
- `gross_profit`, `net_margin`
- `uplift_vs_non_promo` - Percentage uplift from promotions

**Use Cases**:

- Measure promotional ROI by category
- Compare promo vs non-promo performance
- Optimize discount strategies
- Track margin erosion from promotions

#### 6. kpi_dashboard.csv

**Purpose**: High-level KPIs aligned with strategic recommendations.

**Key Fields**:

- `reactivation_rate` - % of previously declining products now growing/plateau
- `weekly_revenue`, `vs_baseline_revenue_lift_pct`
- `promotional_roi` - Revenue / discount spend ratio
- `avg_order_value`, `vs_baseline_aov_pct`
- `gross_profit_margin_pct`
- `declining_product_count`, `high_margin_declining_count`
- `seasonal_event_active` (boolean)

**Use Cases**:

- Executive dashboard monitoring
- Track strategic KPIs from marketing report
- Monitor overall business health
- Measure campaign effectiveness

#### 7. campaign_timeline_reference.csv

**Purpose**: Static reference table for recommended campaign phases.

**Key Fields**:

- `campaign_phase` - Campaign name (e.g., "Black Friday/Cyber Monday")
- `start_date`, `end_date`, `duration_days`
- `target_audience`, `target_products`, `channels`, `messaging_theme`
- `recommended_categories`, `discount_range`

**Use Cases**:

- Reference table for Tableau dashboard filters
- Campaign planning timeline
- Budget allocation guidance
- Channel strategy recommendations

### Regenerating Processed Data

If you update the interim data or need to regenerate the processed datasets:

```bash
python3 src/services/create_tableau_datasets.py
```

The script will:

1. Load `data/interim/featured_data.csv` and `data/interim/calendar_events.csv`
2. Load product/brand dimensions from `data/raw/`
3. Aggregate daily data to weekly periods (Monday-start weeks)
4. Calculate derived metrics (trends, baselines, lifts)
5. Generate all 7 CSV files in `data/processed/`
6. Display summary statistics

**Data Quality Checks**:

- Date range: Oct 17, 2022 - Oct 16, 2025 (3 years)
- Weekly periods: ~158 weeks
- Product count: 457 unique products
- Categories: 5 (Accessories, Grooming, Wellness, Toys, Treats)
- No null values in critical fields

## Project Structure

```text
tailwagg/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Database setup
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
│
├── 📁 data/                     # Data storage
│   ├── 📁 raw/                  # Original data (dimension tables)
│   ├── 📁 interim/              # Intermediate data (featured_data.csv, calendar_events.csv)
│   ├── 📁 processed/            # Tableau dashboard datasets (7 CSV files)
│   └── 📁 schema/               # Database schema
│       └── schema.sql        # SQL schema definition
│
├── 📁 notebooks/                # Jupyter notebooks
│   ├── 1.0-pdr-initial-data-exploration.ipynb        # Initial data exploration
│   ├── 2.0-pdr-calendar-events-analysis.ipynb        # Holiday and event analysis
│   ├── 3.0-pdr-product-performance-analysis.ipynb    # Product performance analysis
│   ├── 4.0-pdr-feature-engineering.ipynb             # Feature engineering
│   └── 5.0-pdr-final-insights-visualization.ipynb    # Final insights and recommendations
│
├── 📁 reports/                  # Generated reports
│   ├── 📁 figures/             # Charts and graphs
│   │   └── ERD.svg          # Database diagram
│   └── TailWagg_Marketing_Analysis_Report.md  # Final report
│
└── 📁 src/                      # Source code
    ├── __init__.py          # Package initialization
    ├── config.py            # Configuration settings
    ├── dataset.py           # Data loading utilities
    ├── features.py          # Feature engineering
    ├── plots.py             # Visualization functions
    │
    ├── 📁 services/            # Data services
    │   ├── __init__.py
    │   ├── create_schema.py # Database setup
    │   ├── generate_data.py # Data generation
    │   └── create_tableau_datasets.py # Tableau dataset generation
    │
    └── 📁 utils/               # Utilities
        ├── __init__.py
        ├── database.py      # Database utilities
        ├── validation.py    # Input validation
        └── notebook_helpers.py  # Notebook utilities
```

## Notebooks Guide

### 1. Initial Data Exploration (`1.0-pdr-initial-data-exploration.ipynb`)

**Purpose**: Basic data exploration and quality checks

**Key Sections**:

- Database connection setup
- Data loading and inspection
- Basic product analysis
- Data quality checks

**Run Time**: ~2-3 minutes

### 2. Calendar Events Analysis (`2.0-pdr-calendar-events-analysis.ipynb`)

**Purpose**: Holiday and seasonal event analysis

**Key Sections**:

- US federal holidays
- Pet industry events
- Seasonal event flagging
- Event categorization
- Pre-holiday analysis

**Run Time**: ~1-2 minutes

### 3. Product Performance Analysis (`3.0-pdr-product-performance-analysis.ipynb`)

**Purpose**: Product-specific performance analysis

**Key Sections**:

- Product intelligence dataset creation
- Individual product metrics
- Category performance
- Brand analysis
- Top performing products

**Run Time**: ~3-5 minutes

### 4. Feature Engineering (`4.0-pdr-feature-engineering.ipynb`)

**Purpose**: Data preprocessing and feature creation

**Key Sections**:

- Rolling average calculations
- Trend calculations
- Data preprocessing functions
- Feature creation utilities

**Run Time**: ~2-3 minutes

### 5. Final Insights Visualization (`5.0-pdr-final-insights-visualization.ipynb`)

**Purpose**: Business insights and actionable recommendations

**Key Sections**:

- Product performance trend analysis
- Reactivation target identification
- Seasonal event performance
- High-margin declining products
- Marketing channel recommendations

**Run Time**: ~2-5 minutes

## API Reference

### Data Loading

```python
from src.dataset import load_product_intelligence, load_daily_metrics

# Load main dataset
df = load_product_intelligence()

# Load daily metrics
daily_df = load_daily_metrics()
```

### Feature Engineering

```python
from src.features import calculate_rolling_averages, calculate_trend_labels

# Calculate rolling averages
df_with_rolling = calculate_rolling_averages(df, windows=[30, 90])

# Add trend labels
df_with_trends = calculate_trend_labels(df_with_rolling)
```

### Visualizations

```python
from src.plots import plot_declining_products, plot_trend_distribution

# Create declining products plot
fig = plot_declining_products(df)

# Create trend distribution plot
fig = plot_trend_distribution(df)
```

### Database Utilities

```python
from src.utils import get_database_engine, test_connection

# Get database engine
engine = get_database_engine()

# Test connection
is_connected = test_connection(engine)
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**:

```bash
# Check if Docker is running
docker compose ps

# Restart database
docker compose down
docker compose up -d

# Check logs
docker compose logs postgres_main
```

#### 2. Missing Environment Variables

**Error**: `ValueError: Missing required environment variables`

**Solution**:

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

#### 3. Import Errors

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:

```bash
# Install package in development mode
pip install -e .

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 4. Jupyter Kernel Issues

**Error**: `Kernel died` or `Notebook controller is disposed`

**Solution**:

```bash
# Restart Jupyter kernel
# In Jupyter: Kernel -> Restart

# Or restart Jupyter server
jupyter notebook --generate-config
jupyter notebook
```

## Author

- **Paul Rodriguez** - *Initial work* - [@paulrodriguez](https://github.com/paulrodriguez)

## Acknowledgments

- DataCamp for the project inspiration
- The open-source community for excellent tools and libraries
