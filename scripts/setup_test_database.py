"""Script to set up PostgreSQL test database with dummy data.

This script creates and populates a star schema database for vehicle market share analysis.
It implements the schema defined in docs/VEHICLE_MARKET_STAR_SCHEMA.md, including:
- Dimension tables for time, OEMs, vehicles, and geography
- Fact tables for market share at country and district levels
- Sample data for testing and development

The schema follows these design principles:
1. Proper normalization of dimension tables
2. Referential integrity through foreign key constraints
3. Appropriate data types and constraints
4. Support for both country and district-level analytics

Usage:
    python scripts/setup_test_database.py

Requirements:
    - PostgreSQL server running locally
    - psycopg2-binary package installed
    - Appropriate database permissions
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime, date
from typing import Dict, Any

# Configure logging with timestamp and level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Test database configuration
# These values can be overridden using environment variables in production
TEST_DB_CONFIG = {
    'host': 'localhost',      # Database server address
    'port': 5432,            # Default PostgreSQL port
    'database': 'market_share_test',  # Database name
    'user': 'postgres',      # Database user
    'password': 'postgres',  # Database password (use environment variables in production)
}

def create_tables(conn) -> None:
    """Create the star schema tables.
    
    This function creates all necessary tables for the vehicle market share star schema:
    
    Dimension Tables:
    - DimTime: Temporal dimension for time-based analysis
    - DimOEM: Original Equipment Manufacturer information
    - DimVehicle: Vehicle characteristics (body type, fuel type)
    - DimGeographyCountry: Country-level geographic information
    - DimGeographyDistrict: District-level geographic information
    
    Fact Tables:
    - FactMarketShareCountry: Market share metrics at country level
    - FactMarketShareDistrict: Market share metrics at district level
    
    Args:
        conn: psycopg2 database connection object
    
    Note:
        - All tables use 'IF NOT EXISTS' to avoid errors on repeated runs
        - Foreign key constraints ensure referential integrity
        - Appropriate data types are used (DECIMAL for market share, etc.)
    """
    with conn.cursor() as cur:
        # Create DimTime
        # time_key format: YYYYMM (e.g., 202301 for January 2023)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS DimTime (
            time_key INTEGER PRIMARY KEY,
            year_report INTEGER NOT NULL,
            month_report INTEGER NOT NULL,
            year_month DATE NOT NULL,
            quarter INTEGER NOT NULL,
            year_quarter VARCHAR(7) NOT NULL
        )
        """)
        
        # Create DimOEM
        # Stores manufacturer details including category (Luxury, Mass Market, etc.)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS DimOEM (
            oem_key SERIAL PRIMARY KEY,
            oem_name VARCHAR(100) NOT NULL UNIQUE,
            oem_category VARCHAR(50) NOT NULL,
            country_origin VARCHAR(50) NOT NULL
        )
        """)
        
        # Create DimVehicle
        # Combines body type and fuel type characteristics
        cur.execute("""
        CREATE TABLE IF NOT EXISTS DimVehicle (
            vehicle_key SERIAL PRIMARY KEY,
            body_type VARCHAR(50) NOT NULL,
            fuel_type VARCHAR(50) NOT NULL,
            vehicle_desc VARCHAR(150) NOT NULL
        )
        """)
        
        # Create DimGeographyCountry
        # Country-level geography with ISO codes
        cur.execute("""
        CREATE TABLE IF NOT EXISTS DimGeographyCountry (
            geography_country_key SERIAL PRIMARY KEY,
            country_name VARCHAR(100) NOT NULL UNIQUE,
            country_code VARCHAR(3) NOT NULL
        )
        """)
        
        # Create DimGeographyDistrict
        # District-level geography with full location hierarchy
        cur.execute("""
        CREATE TABLE IF NOT EXISTS DimGeographyDistrict (
            geography_district_key SERIAL PRIMARY KEY,
            country_name VARCHAR(100) NOT NULL,
            country_code VARCHAR(3) NOT NULL,
            region_name VARCHAR(100),
            district_postcode VARCHAR(20),
            district_town_name VARCHAR(100),
            full_location_path VARCHAR(500) NOT NULL
        )
        """)
        
        # Create FactMarketShareCountry
        # Market share facts at country level
        cur.execute("""
        CREATE TABLE IF NOT EXISTS FactMarketShareCountry (
            fact_country_key SERIAL PRIMARY KEY,
            time_key INTEGER NOT NULL REFERENCES DimTime(time_key),
            oem_key INTEGER NOT NULL REFERENCES DimOEM(oem_key),
            vehicle_key INTEGER NOT NULL REFERENCES DimVehicle(vehicle_key),
            geography_country_key INTEGER NOT NULL REFERENCES DimGeographyCountry(geography_country_key),
            total_vehicles_country INTEGER NOT NULL,
            total_vehicles_country_oem INTEGER NOT NULL,
            market_share_country DECIMAL(8,6) NOT NULL
        )
        """)
        
        # Create FactMarketShareDistrict
        # Market share facts at district level
        cur.execute("""
        CREATE TABLE IF NOT EXISTS FactMarketShareDistrict (
            fact_district_key SERIAL PRIMARY KEY,
            time_key INTEGER NOT NULL REFERENCES DimTime(time_key),
            oem_key INTEGER NOT NULL REFERENCES DimOEM(oem_key),
            vehicle_key INTEGER NOT NULL REFERENCES DimVehicle(vehicle_key),
            geography_district_key INTEGER NOT NULL REFERENCES DimGeographyDistrict(geography_district_key),
            total_vehicles_district INTEGER NOT NULL,
            total_vehicles_district_oem INTEGER NOT NULL,
            market_share_district DECIMAL(8,6) NOT NULL
        )
        """)
        
        conn.commit()
        logging.info("Created all tables successfully")

def insert_test_data(conn) -> None:
    """Insert test data into the star schema tables.
    
    This function populates all dimension and fact tables with comprehensive sample data:
    
    Sample Data Overview:
    - Time: First quarter of 2023 (Jan-Mar)
    - OEMs: BMW (Luxury), Toyota (Mass Market), Mercedes-Benz (Luxury)
    - Vehicles: Electric Sedan, Hybrid SUV, Gasoline Compact
    - Geography: Germany, France, England with major cities
    
    Market Share Patterns:
    - Luxury brands (BMW, Mercedes) have higher shares in wealthy districts
    - Mass market (Toyota) leads in overall volume
    - Electric vehicles show growth in urban areas
    - Hybrid SUVs popular across all regions
    - Regional variations reflect local preferences
    
    Args:
        conn: psycopg2 database connection object
    """
    with conn.cursor() as cur:
        # Insert DimTime test data - First quarter of 2023
        cur.execute("""
        INSERT INTO DimTime (time_key, year_report, month_report, year_month, quarter, year_quarter)
        VALUES 
            (202301, 2023, 1, '2023-01-01', 1, '2023-Q1'),
            (202302, 2023, 2, '2023-02-01', 1, '2023-Q1'),
            (202303, 2023, 3, '2023-03-01', 1, '2023-Q1')
        ON CONFLICT (time_key) DO NOTHING
        """)
        
        # Insert DimOEM test data
        cur.execute("""
        INSERT INTO DimOEM (oem_name, oem_category, country_origin)
        VALUES 
            ('BMW', 'Luxury', 'Germany'),
            ('Toyota', 'Mass Market', 'Japan'),
            ('Mercedes-Benz', 'Luxury', 'Germany')
        ON CONFLICT (oem_name) DO NOTHING
        RETURNING oem_key, oem_name;
        """)
        oems = {row[1]: row[0] for row in cur.fetchall()}
        
        # Insert DimVehicle test data
        cur.execute("""
        INSERT INTO DimVehicle (body_type, fuel_type, vehicle_desc)
        VALUES 
            ('SEDAN', 'ELECTRIC', 'SEDAN ELECTRIC'),
            ('SUV', 'HYBRID', 'SUV HYBRID'),
            ('COMPACT', 'GASOLINE', 'COMPACT GASOLINE')
        RETURNING vehicle_key, vehicle_desc;
        """)
        vehicles = {row[1]: row[0] for row in cur.fetchall()}
        
        # Insert DimGeographyCountry test data
        cur.execute("""
        INSERT INTO DimGeographyCountry (country_name, country_code)
        VALUES 
            ('Germany', 'DEU'),
            ('France', 'FRA'),
            ('England', 'GBR')
        ON CONFLICT (country_name) DO NOTHING
        RETURNING geography_country_key, country_name;
        """)
        countries = {row[1]: row[0] for row in cur.fetchall()}
        
        # Insert DimGeographyDistrict test data
        cur.execute("""
        INSERT INTO DimGeographyDistrict (
            country_name, country_code, region_name, 
            district_postcode, district_town_name, full_location_path
        )
        VALUES 
            ('Germany', 'DEU', 'Bavaria', '80331', 'Munich', 'Germany/Bavaria/Munich'),
            ('France', 'FRA', 'Ile-de-France', '75001', 'Paris', 'France/Ile-de-France/Paris'),
            ('England', 'GBR', 'Greater London', 'SW1A 1AA', 'London', 'England/Greater London/London')
        RETURNING geography_district_key, district_town_name;
        """)
        districts = {row[1]: row[0] for row in cur.fetchall()}
        
        # Market share data patterns:
        # - Luxury brands stronger in wealthy cities
        # - Mass market leads in volume
        # - Electric vehicles popular in urban areas
        # - Hybrid SUVs have consistent demand
        market_share_data = [
            # January 2023 - Country Level
            # Germany
            (202301, 'BMW', 'SEDAN ELECTRIC', 'Germany', 2000, 400, 0.20),        # 20% luxury EV
            (202301, 'BMW', 'SUV HYBRID', 'Germany', 3000, 450, 0.15),            # 15% luxury hybrid
            (202301, 'Mercedes-Benz', 'SEDAN ELECTRIC', 'Germany', 2000, 360, 0.18), # 18% luxury EV
            (202301, 'Mercedes-Benz', 'SUV HYBRID', 'Germany', 3000, 390, 0.13),    # 13% luxury hybrid
            (202301, 'Toyota', 'COMPACT GASOLINE', 'Germany', 5000, 1500, 0.30),    # 30% mass market
            (202301, 'Toyota', 'SUV HYBRID', 'Germany', 3000, 900, 0.30),           # 30% mass market hybrid
            
            # France
            (202301, 'BMW', 'SEDAN ELECTRIC', 'France', 1800, 270, 0.15),
            (202301, 'BMW', 'SUV HYBRID', 'France', 2500, 375, 0.15),
            (202301, 'Mercedes-Benz', 'SEDAN ELECTRIC', 'France', 1800, 252, 0.14),
            (202301, 'Mercedes-Benz', 'SUV HYBRID', 'France', 2500, 325, 0.13),
            (202301, 'Toyota', 'COMPACT GASOLINE', 'France', 4500, 1575, 0.35),
            (202301, 'Toyota', 'SUV HYBRID', 'France', 2500, 875, 0.35),
            
            # England
            (202301, 'BMW', 'SEDAN ELECTRIC', 'England', 2200, 440, 0.20),
            (202301, 'BMW', 'SUV HYBRID', 'England', 2800, 448, 0.16),
            (202301, 'Mercedes-Benz', 'SEDAN ELECTRIC', 'England', 2200, 418, 0.19),
            (202301, 'Mercedes-Benz', 'SUV HYBRID', 'England', 2800, 420, 0.15),
            (202301, 'Toyota', 'COMPACT GASOLINE', 'England', 4800, 1248, 0.26),
            (202301, 'Toyota', 'SUV HYBRID', 'England', 2800, 784, 0.28),
        ]
        
        # Insert country-level market share data
        for time_key, oem, vehicle, country, total, oem_total, share in market_share_data:
            cur.execute("""
            INSERT INTO FactMarketShareCountry (
                time_key, oem_key, vehicle_key, geography_country_key,
                total_vehicles_country, total_vehicles_country_oem, market_share_country
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                time_key,
                oems[oem],
                vehicles[vehicle],
                countries[country],
                total,
                oem_total,
                share
            ))
        
        # District-level market share data (50% of country volume for capital cities)
        district_share_data = [
            # Munich - Higher luxury share
            (202301, 'BMW', 'SEDAN ELECTRIC', 'Munich', 1000, 240, 0.24),        # 24% luxury EV
            (202301, 'BMW', 'SUV HYBRID', 'Munich', 1500, 270, 0.18),            # 18% luxury hybrid
            (202301, 'Mercedes-Benz', 'SEDAN ELECTRIC', 'Munich', 1000, 220, 0.22),
            (202301, 'Mercedes-Benz', 'SUV HYBRID', 'Munich', 1500, 255, 0.17),
            (202301, 'Toyota', 'COMPACT GASOLINE', 'Munich', 2500, 625, 0.25),
            (202301, 'Toyota', 'SUV HYBRID', 'Munich', 1500, 360, 0.24),
            
            # Paris - Strong EV adoption
            (202301, 'BMW', 'SEDAN ELECTRIC', 'Paris', 900, 180, 0.20),
            (202301, 'BMW', 'SUV HYBRID', 'Paris', 1250, 225, 0.18),
            (202301, 'Mercedes-Benz', 'SEDAN ELECTRIC', 'Paris', 900, 171, 0.19),
            (202301, 'Mercedes-Benz', 'SUV HYBRID', 'Paris', 1250, 200, 0.16),
            (202301, 'Toyota', 'COMPACT GASOLINE', 'Paris', 2250, 675, 0.30),
            (202301, 'Toyota', 'SUV HYBRID', 'Paris', 1250, 400, 0.32),
            
            # London - Balanced market
            (202301, 'BMW', 'SEDAN ELECTRIC', 'London', 1100, 242, 0.22),
            (202301, 'BMW', 'SUV HYBRID', 'London', 1400, 252, 0.18),
            (202301, 'Mercedes-Benz', 'SEDAN ELECTRIC', 'London', 1100, 231, 0.21),
            (202301, 'Mercedes-Benz', 'SUV HYBRID', 'London', 1400, 238, 0.17),
            (202301, 'Toyota', 'COMPACT GASOLINE', 'London', 2400, 648, 0.27),
            (202301, 'Toyota', 'SUV HYBRID', 'London', 1400, 434, 0.31),
        ]
        
        # Insert district-level market share data
        for time_key, oem, vehicle, district, total, oem_total, share in district_share_data:
            cur.execute("""
            INSERT INTO FactMarketShareDistrict (
                time_key, oem_key, vehicle_key, geography_district_key,
                total_vehicles_district, total_vehicles_district_oem, market_share_district
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                time_key,
                oems[oem],
                vehicles[vehicle],
                districts[district],
                total,
                oem_total,
                share
            ))
        
        conn.commit()
        logging.info("Inserted comprehensive test data successfully")

def test_queries(conn) -> None:
    """Run test queries to verify the data and demonstrate typical analytics.
    
    This function runs sample analytical queries that:
    1. Calculate market share by manufacturer
    2. Analyze district-level performance
    
    Args:
        conn: psycopg2 database connection object
    
    Note:
        - Uses RealDictCursor for more readable results
        - Formats output for easy verification
        - Demonstrates typical BI queries
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Test query 1: Get market share by OEM
        # Demonstrates manufacturer performance analysis
        cur.execute("""
        SELECT 
            o.oem_name,
            AVG(f.market_share_country) as avg_market_share,
            SUM(f.total_vehicles_country_oem) as total_vehicles
        FROM FactMarketShareCountry f
        JOIN DimOEM o ON f.oem_key = o.oem_key
        GROUP BY o.oem_name
        ORDER BY avg_market_share DESC
        """)
        results = cur.fetchall()
        logging.info("Market share by OEM:")
        for row in results:
            logging.info(f"  {row['oem_name']}: {row['avg_market_share']:.2%} ({row['total_vehicles']} vehicles)")
        
        # Test query 2: Get district-level data
        # Demonstrates geographic performance analysis
        cur.execute("""
        SELECT 
            g.country_name,
            g.district_town_name,
            f.total_vehicles_district,
            f.market_share_district
        FROM FactMarketShareDistrict f
        JOIN DimGeographyDistrict g ON f.geography_district_key = g.geography_district_key
        ORDER BY f.market_share_district DESC
        """)
        results = cur.fetchall()
        logging.info("\nDistrict-level market share:")
        for row in results:
            logging.info(f"  {row['district_town_name']}, {row['country_name']}: {row['market_share_district']:.2%}")

def main():
    """Main function to set up and test the database.
    
    This function:
    1. Establishes database connection
    2. Creates the star schema tables
    3. Populates tables with test data
    4. Runs verification queries
    5. Handles errors and cleanup
    
    The function uses a try-except block to ensure proper error handling
    and logging of any issues that occur during the setup process.
    """
    try:
        # Connect to PostgreSQL
        logging.info(f"Connecting to PostgreSQL at {TEST_DB_CONFIG['host']}:{TEST_DB_CONFIG['port']}")
        conn = psycopg2.connect(**TEST_DB_CONFIG)
        
        # Create tables
        logging.info("Creating tables...")
        create_tables(conn)
        
        # Insert test data
        logging.info("Inserting test data...")
        insert_test_data(conn)
        
        # Run test queries
        logging.info("Running test queries...")
        test_queries(conn)
        
        conn.close()
        logging.info("Database setup and testing completed successfully")
        
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main() 