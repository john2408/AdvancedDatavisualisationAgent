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
    
    This function populates all dimension and fact tables with sample data:
    
    Sample Data Overview:
    - Time: First quarter of 2023 (Jan-Mar)
    - OEMs: BMW (Luxury), Toyota (Mass Market), Mercedes-Benz (Luxury)
    - Vehicles: Electric Sedan, Hybrid SUV, Gasoline Compact
    - Geography: Germany, France, England with major cities
    
    Market Share Data:
    - Country level: 25% market share (250 out of 1000 vehicles)
    - District level: 20% market share (100 out of 500 vehicles)
    
    Args:
        conn: psycopg2 database connection object
    
    Note:
        - Uses ON CONFLICT clauses to handle duplicate insertions
        - Maintains referential integrity in fact tables
        - Provides realistic but simplified test scenarios
    """
    with conn.cursor() as cur:
        # Insert DimTime test data
        # First quarter of 2023 for initial testing
        cur.execute("""
        INSERT INTO DimTime (time_key, year_report, month_report, year_month, quarter, year_quarter)
        VALUES 
            (202301, 2023, 1, '2023-01-01', 1, '2023-Q1'),
            (202302, 2023, 2, '2023-02-01', 1, '2023-Q1'),
            (202303, 2023, 3, '2023-03-01', 1, '2023-Q1')
        ON CONFLICT (time_key) DO NOTHING
        """)
        
        # Insert DimOEM test data
        # Mix of luxury and mass market manufacturers
        cur.execute("""
        INSERT INTO DimOEM (oem_name, oem_category, country_origin)
        VALUES 
            ('BMW', 'Luxury', 'Germany'),
            ('Toyota', 'Mass Market', 'Japan'),
            ('Mercedes-Benz', 'Luxury', 'Germany')
        ON CONFLICT (oem_name) DO NOTHING
        """)
        
        # Insert DimVehicle test data
        # Different combinations of body types and fuel types
        cur.execute("""
        INSERT INTO DimVehicle (body_type, fuel_type, vehicle_desc)
        VALUES 
            ('SEDAN', 'ELECTRIC', 'SEDAN ELECTRIC'),
            ('SUV', 'HYBRID', 'SUV HYBRID'),
            ('COMPACT', 'GASOLINE', 'COMPACT GASOLINE')
        """)
        
        # Insert DimGeographyCountry test data
        # Major European markets
        cur.execute("""
        INSERT INTO DimGeographyCountry (country_name, country_code)
        VALUES 
            ('Germany', 'DEU'),
            ('France', 'FRA'),
            ('England', 'GBR')
        ON CONFLICT (country_name) DO NOTHING
        """)
        
        # Insert DimGeographyDistrict test data
        # Major cities in each country
        cur.execute("""
        INSERT INTO DimGeographyDistrict (
            country_name, country_code, region_name, 
            district_postcode, district_town_name, full_location_path
        )
        VALUES 
            ('Germany', 'DEU', 'Bavaria', '80331', 'Munich', 'Germany/Bavaria/Munich'),
            ('France', 'FRA', 'Ile-de-France', '75001', 'Paris', 'France/Ile-de-France/Paris'),
            ('England', 'GBR', 'Greater London', 'SW1A 1AA', 'London', 'England/Greater London/London')
        """)
        
        # Get the keys for our fact table insertions
        cur.execute("SELECT time_key FROM DimTime LIMIT 1")
        time_key = cur.fetchone()[0]
        
        cur.execute("SELECT oem_key FROM DimOEM LIMIT 1")
        oem_key = cur.fetchone()[0]
        
        cur.execute("SELECT vehicle_key FROM DimVehicle LIMIT 1")
        vehicle_key = cur.fetchone()[0]
        
        cur.execute("SELECT geography_country_key FROM DimGeographyCountry LIMIT 1")
        geography_country_key = cur.fetchone()[0]
        
        cur.execute("SELECT geography_district_key FROM DimGeographyDistrict LIMIT 1")
        geography_district_key = cur.fetchone()[0]
        
        # Insert FactMarketShareCountry test data
        # Example: 25% market share (250 out of 1000 vehicles)
        cur.execute("""
        INSERT INTO FactMarketShareCountry (
            time_key, oem_key, vehicle_key, geography_country_key,
            total_vehicles_country, total_vehicles_country_oem, market_share_country
        )
        VALUES (%s, %s, %s, %s, 1000, 250, 0.25)
        """, (time_key, oem_key, vehicle_key, geography_country_key))
        
        # Insert FactMarketShareDistrict test data
        # Example: 20% market share (100 out of 500 vehicles)
        cur.execute("""
        INSERT INTO FactMarketShareDistrict (
            time_key, oem_key, vehicle_key, geography_district_key,
            total_vehicles_district, total_vehicles_district_oem, market_share_district
        )
        VALUES (%s, %s, %s, %s, 500, 100, 0.20)
        """, (time_key, oem_key, vehicle_key, geography_district_key))
        
        conn.commit()
        logging.info("Inserted test data successfully")

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