import os
import sys
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from contextlib import contextmanager
from pathlib import Path
from typing import List, Dict, Any

import psycopg2
from psycopg2.extras import execute_batch, Json
from dotenv import load_dotenv


def load_env_variables() -> dict:
    """Load environment variables for database connection and random seed."""
    load_dotenv()
    
    # Database connection
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    
    # Random seed
    random_seed = int(os.getenv("RANDOM_SEED", "42"))
    
    missing = [k for k, v in {"DB_PASSWORD": db_password, "DB_NAME": db_name}.items() if not v]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
    
    return {
        "host": db_host,
        "port": db_port,
        "user": db_user,
        "password": db_password,
        "dbname": db_name,
        "random_seed": random_seed,
    }


@contextmanager
def pg_connection(params: dict):
    """Database connection with retry logic."""
    last_exc = None
    conn = None
    for _ in range(10):
        try:
            conn = psycopg2.connect(**{k: v for k, v in params.items() if k != "random_seed"})
            break
        except Exception as exc:
            last_exc = exc
            import time
            time.sleep(2)
    if conn is None:
        raise last_exc
    try:
        yield conn
    finally:
        conn.close()


def setup_random_seed(seed: int):
    """Set random seeds for reproducible data generation."""
    random.seed(seed)
    np.random.seed(seed)


def generate_dimension_data(start_date: date, end_date: date) -> Dict[str, List[Dict]]:
    """Generate all dimension data."""
    print("Generating dimension data...")
    
    # Categories
    categories = [
        {"category_id": "toys", "category_name": "Toys"},
        {"category_id": "treats", "category_name": "Treats"},
        {"category_id": "grooming", "category_name": "Grooming"},
        {"category_id": "wellness", "category_name": "Wellness"},
        {"category_id": "accessories", "category_name": "Accessories"},
    ]
    
    # Brands
    brands = [
        {"brand_id": "kong", "brand_name": "Kong"},
        {"brand_id": "nylabone", "brand_name": "Nylabone"},
        {"brand_id": "greenies", "brand_name": "Greenies"},
        {"brand_id": "wellness", "brand_name": "Wellness"},
        {"brand_id": "blue_buffalo", "brand_name": "Blue Buffalo"},
        {"brand_id": "purina", "brand_name": "Purina"},
        {"brand_id": "hills", "brand_name": "Hills"},
        {"brand_id": "royal_canin", "brand_name": "Royal Canin"},
    ]
    
    # Channels
    channels = [
        {"channel_id": "online_store", "channel_name": "Online Store", "channel_type": "Owned"},
        {"channel_id": "instore", "channel_name": "Instore", "channel_type": "Owned"},
        {"channel_id": "meta_paid", "channel_name": "Meta Paid", "channel_type": "Paid"},
        {"channel_id": "tiktok_paid", "channel_name": "TikTok Paid", "channel_type": "Paid"},
        {"channel_id": "email", "channel_name": "Email", "channel_type": "Owned"},
        {"channel_id": "sms", "channel_name": "SMS", "channel_type": "Owned"},
        {"channel_id": "amazon", "channel_name": "Amazon", "channel_type": "Earned"},
    ]
    
    # Locations
    locations = [
        {"location_id": "online_us", "location_type": "online", "country": "US", "region": "North America", "store_id": None},
        {"location_id": "online_ca", "location_type": "online", "country": "CA", "region": "North America", "store_id": None},
        {"location_id": "store_nyc", "location_type": "store", "country": "US", "region": "North America", "store_id": "NYC001"},
        {"location_id": "store_la", "location_type": "store", "country": "US", "region": "North America", "store_id": "LA001"},
        {"location_id": "store_toronto", "location_type": "store", "country": "CA", "region": "North America", "store_id": "TOR001"},
    ]
    
    # Generate dynamic promotions for each year
    promos = generate_dynamic_promotions(start_date, end_date)
    
    # Products (600 products)
    products = []
    product_names = [
        "Chew Toy", "Treats", "Shampoo", "Supplements", "Collar", "Leash", "Bed", "Bowl",
        "Food", "Snacks", "Brush", "Toothbrush", "Crate", "Carrier", "Harness", "Tag"
    ]
    sizes = ["XS", "S", "M", "L", "XL"]
    colors = ["Red", "Blue", "Green", "Yellow", "Black", "White", "Brown", "Pink"]
    
    for i in range(600):
        product_id = f"prod_{i+1:03d}"
        category = random.choice(categories)
        brand = random.choice(brands)
        name = f"{random.choice(product_names)} {i+1}"
        
        # Create attributes JSON
        attributes = {
            "size": random.choice(sizes),
            "flavor": random.choice(["Chicken", "Beef", "Salmon", "Turkey", "None"]) if "treat" in name.lower() or "food" in name.lower() else None,
            "color": random.choice(colors),
            "material": random.choice(["Rubber", "Plastic", "Fabric", "Metal", "Wood"])
        }
        
        # Remove None values
        attributes = {k: v for k, v in attributes.items() if v is not None}
        
        products.append({
            "product_id": product_id,
            "sku": f"SKU-{product_id.upper()}",
            "name": name,
            "category_id": category["category_id"],
            "brand_id": brand["brand_id"],
            "is_active": random.choice([True, True, True, False]),  # 75% active
            "attributes": attributes,
            "created_at": datetime.now() - timedelta(days=random.randint(30, 1095)),  # Created 1 month to 3 years ago
            "discontinued_at": None if random.choice([True, True, True, False]) else datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    # Customers (6000 customers)
    customers = []
    loyalty_tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    acquisition_channels = ["Online", "Store", "Referral", "Social Media", "Email"]
    
    for i in range(6000):
        customer_id = f"cust_{i+1:04d}"
        created_at = datetime.now() - timedelta(days=random.randint(1, 1095))  # Last 3 years
        
        # LTV based on loyalty tier and time as customer
        days_since_creation = (datetime.now() - created_at).days
        base_ltv = random.uniform(50, 500)
        if days_since_creation > 365:
            base_ltv *= 1.5
        if days_since_creation > 730:
            base_ltv *= 1.3
        
        customers.append({
            "customer_id": customer_id,
            "created_at": created_at,
            "lifetime_value": round(base_ltv, 2),
            "loyalty_tier": random.choice(loyalty_tiers),
            "email_opt_in": random.choice([True, True, False]),  # 67% opt-in
            "acquisition_channel": random.choice(acquisition_channels)
        })
    
    return {
        "categories": categories,
        "brands": brands,
        "channels": channels,
        "locations": locations,
        "promos": promos,
        "products": products,
        "customers": customers
    }


def get_holiday_multiplier(date_obj: date, year: int) -> float:
    """Get sales multiplier based on holiday seasons with year-over-year variation."""
    month = date_obj.month
    day = date_obj.day
    
    # Year-over-year variation factor (some years are better than others)
    year_factor = 0.8 + (year % 3) * 0.2  # Cycles through 0.8, 1.0, 1.2
    
    # Black Friday / Cyber Monday (November)
    if month == 11 and 24 <= day <= 30:
        base_mult = random.uniform(2.5, 4.0)
        return base_mult * year_factor
    
    # December holiday season
    if month == 12:
        if day <= 15:
            base_mult = random.uniform(1.8, 2.5)
        else:
            base_mult = random.uniform(2.0, 3.0)
        return base_mult * year_factor
    
    # Valentine's Day (February) - varies significantly by year
    if month == 2 and 10 <= day <= 16:
        valentine_variation = random.uniform(0.7, 1.3)  # Some years much better/worse
        base_mult = random.uniform(1.3, 1.8)
        return base_mult * valentine_variation * year_factor
    
    # Mother's Day (May) - also varies by year
    if month == 5 and 8 <= day <= 14:
        mothers_variation = random.uniform(0.8, 1.2)
        base_mult = random.uniform(1.2, 1.6)
        return base_mult * mothers_variation * year_factor
    
    # Summer (June-August) - varies by year and weather patterns
    if month in [6, 7, 8]:
        summer_variation = random.uniform(0.9, 1.3)  # Some summers much better
        base_mult = random.uniform(1.1, 1.4)
        return base_mult * summer_variation * year_factor
    
    # Regular season with weekly variation
    return random.uniform(0.8, 1.2) * year_factor


def get_weekly_variation(date_obj: date) -> float:
    """Get weekly variation factor for more realistic business cycles."""
    # Get week number in year
    week_num = date_obj.isocalendar()[1]
    
    # Create cyclical patterns throughout the year
    # Early year slump (Jan-Feb)
    if week_num <= 8:
        return random.uniform(0.7, 0.9)
    
    # Spring pickup (Mar-May)
    elif week_num <= 20:
        return random.uniform(0.9, 1.1)
    
    # Summer peak (Jun-Aug)
    elif week_num <= 32:
        return random.uniform(1.0, 1.3)
    
    # Fall transition (Sep-Oct)
    elif week_num <= 44:
        return random.uniform(0.8, 1.0)
    
    # Holiday season (Nov-Dec)
    else:
        return random.uniform(1.1, 1.5)


def get_promo_impact(date_obj: date, active_promos: List[Dict]) -> float:
    """Calculate promotional impact based on active campaigns."""
    if not active_promos:
        return 1.0
    
    total_impact = 1.0
    for promo in active_promos:
        promo_type = promo["promo_type"]
        
        # Different promo types have different impact levels
        if promo_type == "discount":
            impact = random.uniform(1.1, 1.4)  # 10-40% boost
        elif promo_type == "BOGO":
            impact = random.uniform(1.3, 1.8)  # 30-80% boost
        elif promo_type == "bundle":
            impact = random.uniform(1.2, 1.6)  # 20-60% boost
        elif promo_type == "coupon":
            impact = random.uniform(1.05, 1.25)  # 5-25% boost
        else:
            impact = 1.0
        
        # Promos can stack but with diminishing returns
        total_impact += (impact - 1.0) * 0.7  # 70% effectiveness when stacked
    
    return min(total_impact, 2.5)  # Cap at 2.5x multiplier


def generate_dynamic_promotions(start_date: date, end_date: date) -> List[Dict]:
    """Generate dynamic promotions that vary by year and season."""
    promos = []
    promo_counter = 1
    
    # Generate promotions for each year
    current_year = start_date.year
    end_year = end_date.year
    
    while current_year <= end_year:
        year = current_year
        
        # Year-specific promotional themes (some years more aggressive)
        year_aggressiveness = random.uniform(0.7, 1.3)
        
        # Holiday promotions (every year)
        # Black Friday/Cyber Monday
        promos.append({
            "promo_id": f"black_friday_{year}",
            "promo_name": f"Black Friday {year} - Up to 50% Off",
            "promo_type": "discount",
            "start_date": f"{year}-11-24",
            "end_date": f"{year}-11-30"
        })
        
        # Christmas/Holiday season
        promos.append({
            "promo_id": f"holiday_season_{year}",
            "promo_name": f"Holiday Season {year} Special",
            "promo_type": "discount",
            "start_date": f"{year}-12-01",
            "end_date": f"{year}-12-31"
        })
        
        # Valentine's Day (varies by year)
        if random.random() < 0.8:  # 80% chance each year
            promos.append({
                "promo_id": f"valentines_{year}",
                "promo_name": f"Valentine's Day {year} - Love Your Pet",
                "promo_type": "discount",
                "start_date": f"{year}-02-10",
                "end_date": f"{year}-02-16"
            })
        
        # Mother's Day (varies by year)
        if random.random() < 0.7:  # 70% chance each year
            promos.append({
                "promo_id": f"mothers_day_{year}",
                "promo_name": f"Mother's Day {year} - Treat Mom's Pet",
                "promo_type": "discount",
                "start_date": f"{year}-05-08",
                "end_date": f"{year}-05-14"
            })
        
        # Summer campaigns (varies by year)
        if random.random() < 0.9:  # 90% chance each year
            promo_type = random.choice(["BOGO", "bundle", "discount"])
            promos.append({
                "promo_id": f"summer_{year}_{promo_counter}",
                "promo_name": f"Summer {year} - {promo_type.title()} Special",
                "promo_type": promo_type,
                "start_date": f"{year}-06-01",
                "end_date": f"{year}-08-31"
            })
            promo_counter += 1
        
        # Back-to-school (August-September)
        if random.random() < 0.6:  # 60% chance each year
            promos.append({
                "promo_id": f"back_to_school_{year}",
                "promo_name": f"Back to School {year} - Pet Prep",
                "promo_type": "bundle",
                "start_date": f"{year}-08-15",
                "end_date": f"{year}-09-15"
            })
        
        # Random flash sales throughout the year (2-4 per year)
        num_flash_sales = random.randint(2, 4)
        for _ in range(num_flash_sales):
            # Random month and duration
            month = random.randint(1, 12)
            duration = random.randint(3, 7)  # 3-7 days
            start_day = random.randint(1, 28)
            
            start_date_str = f"{year}-{month:02d}-{start_day:02d}"
            end_date_str = f"{year}-{month:02d}-{min(start_day + duration, 28):02d}"
            
            promo_type = random.choice(["discount", "BOGO", "coupon"])
            promos.append({
                "promo_id": f"flash_{year}_{promo_counter}",
                "promo_name": f"Flash Sale {year} - {promo_type.title()}",
                "promo_type": promo_type,
                "start_date": start_date_str,
                "end_date": end_date_str
            })
            promo_counter += 1
        
        # New customer acquisition (year-round)
        promos.append({
            "promo_id": f"new_customer_{year}",
            "promo_name": f"New Customer {year} - Welcome Discount",
            "promo_type": "coupon",
            "start_date": f"{year}-01-01",
            "end_date": f"{year}-12-31"
        })
        
        current_year += 1
    
    return promos


def generate_sales_data(dimensions: Dict[str, List[Dict]], start_date: date, end_date: date) -> List[Dict]:
    """Generate 3 years of sales data with realistic business variations."""
    print(f"Generating sales data from {start_date} to {end_date}...")
    
    sales_data = []
    order_id_counter = 1
    
    # Get active products only
    active_products = [p for p in dimensions["products"] if p["is_active"]]
    
    # Create a lookup for active promotions by date
    promos_by_date = {}
    for promo in dimensions["promos"]:
        promo_start = datetime.strptime(promo["start_date"], "%Y-%m-%d").date()
        promo_end = datetime.strptime(promo["end_date"], "%Y-%m-%d").date()
        
        current_date = promo_start
        while current_date <= promo_end:
            if current_date not in promos_by_date:
                promos_by_date[current_date] = []
            promos_by_date[current_date].append(promo)
            current_date += timedelta(days=1)
    
    current_date = start_date
    while current_date <= end_date:
        # Base daily order count (varies by day of week)
        base_orders = 50 if current_date.weekday() < 5 else 30  # Weekdays vs weekends
        
        # Apply all variation factors
        holiday_mult = get_holiday_multiplier(current_date, current_date.year)
        weekly_mult = get_weekly_variation(current_date)
        
        # Get active promotions for this date
        active_promos = promos_by_date.get(current_date, [])
        promo_mult = get_promo_impact(current_date, active_promos)
        
        # Random business fluctuation (some days just better/worse)
        business_fluctuation = random.uniform(0.7, 1.3)
        
        # Calculate final daily orders
        daily_orders = max(1, int(base_orders * holiday_mult * weekly_mult * promo_mult * business_fluctuation))
        
        # Generate orders for this day
        for _ in range(daily_orders):
            order_id = f"order_{order_id_counter:06d}"
            order_id_counter += 1
            
            # Random customer, channel, location
            customer = random.choice(dimensions["customers"])
            channel = random.choice(dimensions["channels"])
            location = random.choice(dimensions["locations"])
            
            # Number of line items per order (varies by season and promotions)
            base_items = random.choices([1, 2, 3, 4, 5], weights=[20, 30, 30, 15, 5])[0]
            
            # More items during promotions
            if active_promos:
                promo_boost = random.choices([0, 1, 2], weights=[60, 30, 10])[0]
                base_items = min(5, base_items + promo_boost)
            
            num_items = base_items
            
            for item_num in range(num_items):
                product = random.choice(active_products)
                
                # Quantity (varies by promotions and season)
                base_quantity = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
                
                # BOGO promotions increase quantity
                if active_promos and any(p["promo_type"] == "BOGO" for p in active_promos):
                    if random.random() < 0.3:  # 30% chance to buy more during BOGO
                        base_quantity = min(3, base_quantity + 1)
                
                quantity = base_quantity
                
                # Price based on product category
                base_price = random.uniform(5, 100)
                if product["category_id"] == "treats":
                    base_price = random.uniform(3, 25)
                elif product["category_id"] == "toys":
                    base_price = random.uniform(8, 50)
                elif product["category_id"] == "wellness":
                    base_price = random.uniform(15, 80)
                
                unit_price = round(base_price, 2)
                
                # Discount logic (more likely during promotions)
                discount_amount = 0
                promo_id = None
                
                # Base discount chance
                discount_chance = 0.2
                
                # Increase discount chance during promotions
                if active_promos:
                    discount_chance = 0.6  # 60% chance during active promotions
                
                if random.random() < discount_chance:
                    # Choose a random active promo for this order
                    if active_promos:
                        chosen_promo = random.choice(active_promos)
                        promo_id = chosen_promo["promo_id"]
                        
                        # Discount amount based on promo type
                        if chosen_promo["promo_type"] == "discount":
                            discount_amount = round(unit_price * random.uniform(0.1, 0.5), 2)
                        elif chosen_promo["promo_type"] == "BOGO":
                            # BOGO: buy one get one free (50% off second item)
                            if quantity >= 2:
                                discount_amount = round(unit_price * 0.5, 2)
                        elif chosen_promo["promo_type"] == "bundle":
                            discount_amount = round(unit_price * random.uniform(0.15, 0.3), 2)
                        elif chosen_promo["promo_type"] == "coupon":
                            discount_amount = round(unit_price * random.uniform(0.05, 0.2), 2)
                    else:
                        # Regular discount
                        discount_amount = round(unit_price * random.uniform(0.1, 0.3), 2)
                
                # COGS (60-80% of unit price)
                cogs = round(unit_price * random.uniform(0.6, 0.8), 2)
                
                # Timestamp (random time during the day)
                hour = random.randint(8, 22)
                minute = random.randint(0, 59)
                timestamp = datetime.combine(current_date, datetime.min.time().replace(hour=hour, minute=minute))
                
                # Return rate (varies by season and product type)
                base_return_rate = 0.05
                
                # Higher return rates during holiday season (gift returns)
                if current_date.month == 12:
                    base_return_rate = 0.08
                elif current_date.month == 1:  # Post-holiday returns
                    base_return_rate = 0.12
                
                # Higher return rates for certain product categories
                if product["category_id"] in ["accessories", "toys"]:
                    base_return_rate *= 1.5
                
                is_returned = random.random() < base_return_rate
                
                sales_data.append({
                    "order_line_id": f"{order_id}_{item_num+1}",
                    "order_id": order_id,
                    "product_id": product["product_id"],
                    "customer_id": customer["customer_id"],
                    "channel_id": channel["channel_id"],
                    "location_id": location["location_id"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount_amount": discount_amount,
                    "promo_id": promo_id,
                    "cogs": cogs,
                    "order_line_timestamp": timestamp,
                    "is_returned": is_returned
                })
        
        current_date += timedelta(days=1)
    
    print(f"Generated {len(sales_data)} sales records")
    return sales_data


def generate_other_fact_data(dimensions: Dict[str, List[Dict]], start_date: date, end_date: date) -> Dict[str, List[Dict]]:
    """Generate ad spend, email, inventory, and returns data."""
    print("Generating supporting fact data...")
    
    # Ad spend data (daily for paid channels)
    paid_channels = [c for c in dimensions["channels"] if c["channel_type"] == "Paid"]
    ad_spend_data = []
    
    current_date = start_date
    while current_date <= end_date:
        for channel in paid_channels:
            # Daily spend varies by channel and season
            base_spend = random.uniform(100, 1000)
            holiday_mult = get_holiday_multiplier(current_date, current_date.year)
            daily_spend = base_spend * holiday_mult
            
            ad_spend_data.append({
                "ad_spend_id": f"ad_{current_date}_{channel['channel_id']}",
                "date": current_date,
                "channel_id": channel["channel_id"],
                "campaign_id": f"campaign_{random.randint(1, 20)}",
                "adset_id": f"adset_{random.randint(1, 50)}",
                "creative_id": f"creative_{random.randint(1, 100)}",
                "impressions": random.randint(10000, 100000),
                "clicks": random.randint(100, 2000),
                "conversions": random.randint(10, 200),
                "spend": round(daily_spend, 2),
                "revenue_attributed": round(daily_spend * random.uniform(1.2, 3.0), 2)
            })
        current_date += timedelta(days=1)
    
    # Email data (daily) - ensure globally unique primary keys via counter
    email_data = []
    email_counter = 1
    current_date = start_date
    while current_date <= end_date:
        # 2-5 email campaigns per day
        num_campaigns = random.randint(2, 5)
        for _ in range(num_campaigns):
            email_data.append({
                "email_event_id": f"email_{current_date.strftime('%Y%m%d')}_{email_counter:03d}",
                "date": current_date,
                "campaign_id": f"email_campaign_{random.randint(1, 50)}",
                "audience_size": random.randint(5000, 50000),
                "sends": random.randint(4000, 45000),
                "opens": random.randint(800, 9000),
                "clicks": random.randint(80, 900),
                "conversions": random.randint(8, 90),
                "revenue_attributed": round(random.uniform(500, 5000), 2)
            })
            email_counter += 1
        current_date += timedelta(days=1)
    
    # Inventory snapshots (weekly)
    inventory_data = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() == 0:  # Monday snapshots
            for product in dimensions["products"][:100]:  # First 100 products
                for location in dimensions["locations"]:
                    on_hand = random.randint(0, 500)
                    available = max(0, on_hand - random.randint(0, 50))
                    
                    inventory_data.append({
                        "snapshot_id": f"inv_{current_date}_{product['product_id']}_{location['location_id']}",
                        "date": current_date,
                        "product_id": product["product_id"],
                        "location_id": location["location_id"],
                        "on_hand": on_hand,
                        "available": available
                    })
        current_date += timedelta(days=1)
    
    return {
        "ad_spend": ad_spend_data,
        "email": email_data,
        "inventory": inventory_data
    }


def generate_returns_from_sales(sales_data: List[Dict]) -> List[Dict]:
    """Create returns fact rows based on sales rows flagged as returned (FK-safe)."""
    reasons = ["Defective", "Wrong Size", "Not as Described", "Changed Mind", "Late Delivery"]
    returns: List[Dict] = []
    counter = 1
    for row in sales_data:
        if not row.get("is_returned"):
            continue
        order_ts: datetime = row["order_line_timestamp"]
        return_dt = order_ts + timedelta(days=random.randint(1, 30))
        refund_amount = round(max(0.0, (row["unit_price"] * row["quantity"]) - row.get("discount_amount", 0.0)), 2)
        returns.append({
            "return_id": f"return_{counter:07d}",
            "order_line_id": row["order_line_id"],
            "product_id": row["product_id"],
            "return_reason": random.choice(reasons),
            "return_timestamp": return_dt,
            "refund_amount": refund_amount,
        })
        counter += 1
    return returns


def insert_data(conn, table_name: str, data: List[Dict]):
    """Insert data into database table."""
    if not data:
        return
    
    print(f"Inserting {len(data)} records into {table_name}...")
    
    # Get column names from first record
    columns = list(data[0].keys())
    placeholders = ", ".join(["%s"] * len(columns))
    columns_str = ", ".join(columns)
    
    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
    
    # Convert data to list of tuples; adapt JSON-like values
    def adapt(value):
        if isinstance(value, (dict, list)):
            return Json(value)
        return value
    
    values = [tuple(adapt(record[col]) for col in columns) for record in data]
    
    with conn.cursor() as cur:
        execute_batch(cur, query, values, page_size=1000)
    conn.commit()


def main():
    """Main function to generate and insert all data."""
    params = load_env_variables()
    
    # Set random seed for reproducible data
    setup_random_seed(params["random_seed"])
    print(f"Using random seed: {params['random_seed']}")
    
    # Date range (3 years)
    end_date = date.today()
    start_date = end_date - timedelta(days=3*365)
    
    with pg_connection(params) as conn:
        # Generate dimension data
        dimensions = generate_dimension_data(start_date, end_date)
        
        # Insert dimensions
        for table_name, data in [
            ("dim_category", dimensions["categories"]),
            ("dim_brand", dimensions["brands"]),
            ("dim_channel", dimensions["channels"]),
            ("dim_location", dimensions["locations"]),
            ("dim_promo", dimensions["promos"]),
            ("dim_product", dimensions["products"]),
            ("dim_customer", dimensions["customers"]),
        ]:
            insert_data(conn, table_name, data)
        
        # Generate and insert sales data
        sales_data = generate_sales_data(dimensions, start_date, end_date)
        insert_data(conn, "fact_sales", sales_data)
        
        # Generate and insert other fact data (excluding returns)
        other_facts = generate_other_fact_data(dimensions, start_date, end_date)
        for table_name, data in [
            ("fact_ad_spend", other_facts["ad_spend"]),
            ("fact_email", other_facts["email"]),
            ("fact_inventory_snapshots", other_facts["inventory"]),
        ]:
            insert_data(conn, table_name, data)

        # Generate returns from actual returned sales lines (FK-safe)
        returns = generate_returns_from_sales(sales_data)
        insert_data(conn, "fact_returns", returns)
    
    print("Data generation completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
