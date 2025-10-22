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
│   ├── 📁 raw/                  # Original data
│   ├── 📁 interim/              # Intermediate data
│   ├── 📁 processed/            # Final datasets
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
    │   └── generate_data.py # Data generation
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
