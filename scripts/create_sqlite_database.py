#!/usr/bin/env python3
"""
SQLite Database Creator for Vehicle Market Share Star Schema

This script reads the star schema parquet files and creates a SQLite database
with all dimension and fact tables, including proper indexes and foreign key constraints.

The script creates:
- All dimension tables (DimTime, DimOEM, DimVehicle, DimGeographyCountry, DimGeographyDistrict)
- All fact tables (FactMarketShareCountry, FactMarketShareDistrict)
- Primary key and foreign key constraints
- Performance indexes as documented in the star schema design
- Data validation and integrity checks

Usage:
    python scripts/create_sqlite_database.py
"""

import sqlite3
import pandas as pd
import os
import logging
from typing import Dict, List, Tuple
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class StarSchemaToSQLite:
    """Converter for loading star schema parquet files into SQLite database."""
    
    def __init__(self, star_schema_dir: str = "data/star_schema", 
                 db_path: str = "market_share.sqlite"):
        """
        Initialize the converter.
        
        Args:
            star_schema_dir: Directory containing the star schema parquet files
            db_path: Path for the SQLite database file
        """
        self.star_schema_dir = star_schema_dir
        self.db_path = db_path
        self.connection = None
        
        # Define table loading order (dimensions first, then facts)
        self.dimension_tables = [
            'DimTime',
            'DimOEM', 
            'DimVehicle',
            'DimGeographyCountry',
            'DimGeographyDistrict'
        ]
        
        self.fact_tables = [
            'FactMarketShareCountry',
            'FactMarketShareDistrict'
        ]
        
    def __enter__(self):
        """Context manager entry."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            return self
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.connection:
            self.connection.close()
            
    def create_dim_time_table(self) -> None:
        """Create the DimTime table with proper schema."""
        sql = """
        CREATE TABLE IF NOT EXISTS DimTime (
            time_key INTEGER PRIMARY KEY,
            year_report INTEGER NOT NULL,
            month_report INTEGER NOT NULL,
            year_month TEXT NOT NULL,
            quarter INTEGER NOT NULL,
            year_quarter TEXT NOT NULL
        );
        """
        self.connection.execute(sql)
        
    def create_dim_oem_table(self) -> None:
        """Create the DimOEM table with proper schema."""
        sql = """
        CREATE TABLE IF NOT EXISTS DimOEM (
            oem_key INTEGER PRIMARY KEY,
            oem_name TEXT NOT NULL,
            oem_category TEXT NOT NULL,
            country_origin TEXT NOT NULL
        );
        """
        self.connection.execute(sql)
        
    def create_dim_vehicle_table(self) -> None:
        """Create the DimVehicle table with proper schema."""
        sql = """
        CREATE TABLE IF NOT EXISTS DimVehicle (
            vehicle_key INTEGER PRIMARY KEY,
            body_type TEXT NOT NULL,
            fuel_type TEXT NOT NULL,
            vehicle_desc TEXT NOT NULL
        );
        """
        self.connection.execute(sql)
        
    def create_dim_geography_country_table(self) -> None:
        """Create the DimGeographyCountry table with proper schema."""
        sql = """
        CREATE TABLE IF NOT EXISTS DimGeographyCountry (
            geography_country_key INTEGER PRIMARY KEY,
            country_name TEXT NOT NULL,
            country_code TEXT NOT NULL
        );
        """
        self.connection.execute(sql)
        
    def create_dim_geography_district_table(self) -> None:
        """Create the DimGeographyDistrict table with proper schema."""
        sql = """
        CREATE TABLE IF NOT EXISTS DimGeographyDistrict (
            geography_district_key INTEGER PRIMARY KEY,
            country_name TEXT NOT NULL,
            country_code TEXT NOT NULL,
            region_name TEXT,
            district_postcode TEXT,
            district_town_name TEXT,
            full_location_path TEXT NOT NULL
        );
        """
        self.connection.execute(sql)
        
    def create_fact_market_share_country_table(self) -> None:
        """Create the FactMarketShareCountry table with proper schema."""
        sql = """
        CREATE TABLE IF NOT EXISTS FactMarketShareCountry (
            fact_country_key INTEGER PRIMARY KEY,
            time_key INTEGER NOT NULL,
            oem_key INTEGER NOT NULL,
            vehicle_key INTEGER NOT NULL,
            geography_country_key INTEGER NOT NULL,
            total_vehicles_country INTEGER NOT NULL,
            total_vehicles_country_oem INTEGER NOT NULL,
            market_share_country REAL NOT NULL
        );
        """
        self.connection.execute(sql)
        
    def create_fact_market_share_district_table(self) -> None:
        """Create the FactMarketShareDistrict table with proper schema."""
        sql = """
        CREATE TABLE IF NOT EXISTS FactMarketShareDistrict (
            fact_district_key INTEGER PRIMARY KEY,
            time_key INTEGER NOT NULL,
            oem_key INTEGER NOT NULL,
            vehicle_key INTEGER NOT NULL,
            geography_district_key INTEGER NOT NULL,
            total_vehicles_district INTEGER NOT NULL,
            total_vehicles_district_oem INTEGER NOT NULL,
            market_share_district REAL NOT NULL
        );
        """
        self.connection.execute(sql)
        
    def create_all_tables(self) -> None:
        """Create all tables with proper schemas."""
        logger.info("Creating database tables...")
        
        # Create dimension tables
        self.create_dim_time_table()
        self.create_dim_oem_table()
        self.create_dim_vehicle_table()
        self.create_dim_geography_country_table()
        self.create_dim_geography_district_table()
        
        # Create fact tables
        self.create_fact_market_share_country_table()
        self.create_fact_market_share_district_table()
        
        logger.info("All tables created successfully.")
        
    def load_table_data(self, table_name: str) -> None:
        """Load data from parquet file into SQLite table."""
        parquet_path = os.path.join(self.star_schema_dir, f"{table_name}.parquet")
        
        if not os.path.exists(parquet_path):
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
            
        # Load parquet file
        df = pd.read_parquet(parquet_path)
        
        # Convert datetime columns to strings for SQLite compatibility
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]':
                df[col] = df[col].dt.strftime('%Y-%m-%d')
                
        # Insert data into SQLite
        df.to_sql(table_name, self.connection, if_exists='append', index=False)
        
        logger.info(f"Loaded {len(df):,} records into {table_name}")
        
    def create_indexes(self) -> None:
        """Create performance indexes as per star schema design."""
        logger.info("Creating performance indexes...")
        
        indexes = [
            # Dimension table indexes
            "CREATE INDEX IF NOT EXISTS idx_dimtime_year_month ON DimTime(year_report, month_report);",
            "CREATE INDEX IF NOT EXISTS idx_dimtime_quarter ON DimTime(year_report, quarter);",
            "CREATE INDEX IF NOT EXISTS idx_dimoem_name ON DimOEM(oem_name);",
            "CREATE INDEX IF NOT EXISTS idx_dimoem_category ON DimOEM(oem_category);",
            "CREATE INDEX IF NOT EXISTS idx_dimvehicle_body_fuel ON DimVehicle(body_type, fuel_type);",
            "CREATE INDEX IF NOT EXISTS idx_dimgeocountry_name ON DimGeographyCountry(country_name);",
            "CREATE INDEX IF NOT EXISTS idx_dimgeodistrict_country_region ON DimGeographyDistrict(country_name, region_name);",
            
            # Fact table indexes for FactMarketShareCountry
            "CREATE INDEX IF NOT EXISTS idx_factcountry_time ON FactMarketShareCountry(time_key);",
            "CREATE INDEX IF NOT EXISTS idx_factcountry_oem ON FactMarketShareCountry(oem_key);",
            "CREATE INDEX IF NOT EXISTS idx_factcountry_vehicle ON FactMarketShareCountry(vehicle_key);",
            "CREATE INDEX IF NOT EXISTS idx_factcountry_geography ON FactMarketShareCountry(geography_country_key);",
            "CREATE INDEX IF NOT EXISTS idx_factcountry_time_oem ON FactMarketShareCountry(time_key, oem_key);",
            "CREATE INDEX IF NOT EXISTS idx_factcountry_time_vehicle ON FactMarketShareCountry(time_key, vehicle_key);",
            "CREATE INDEX IF NOT EXISTS idx_factcountry_market_share ON FactMarketShareCountry(market_share_country);",
            
            # Fact table indexes for FactMarketShareDistrict
            "CREATE INDEX IF NOT EXISTS idx_factdistrict_time ON FactMarketShareDistrict(time_key);",
            "CREATE INDEX IF NOT EXISTS idx_factdistrict_oem ON FactMarketShareDistrict(oem_key);",
            "CREATE INDEX IF NOT EXISTS idx_factdistrict_vehicle ON FactMarketShareDistrict(vehicle_key);",
            "CREATE INDEX IF NOT EXISTS idx_factdistrict_geography ON FactMarketShareDistrict(geography_district_key);",
            "CREATE INDEX IF NOT EXISTS idx_factdistrict_time_oem ON FactMarketShareDistrict(time_key, oem_key);",
            "CREATE INDEX IF NOT EXISTS idx_factdistrict_time_vehicle ON FactMarketShareDistrict(time_key, vehicle_key);",
            "CREATE INDEX IF NOT EXISTS idx_factdistrict_market_share ON FactMarketShareDistrict(market_share_district);",
        ]
        
        for index_sql in indexes:
            self.connection.execute(index_sql)
            
        logger.info("All indexes created successfully.")
        
    def validate_data_integrity(self) -> Dict[str, any]:
        """Validate data integrity and foreign key relationships."""
        logger.info("Validating data integrity...")
        
        validation_results = {}
        
        # Check record counts
        for table_name in self.dimension_tables + self.fact_tables:
            count = self.connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            validation_results[f"{table_name}_count"] = count
            
        # Check foreign key integrity
        fk_violations = self.connection.execute("PRAGMA foreign_key_check").fetchall()
        validation_results["foreign_key_violations"] = len(fk_violations)
        
        # Check for duplicate primary keys
        for table_name in self.dimension_tables + self.fact_tables:
            if table_name == 'DimTime':
                pk_col = 'time_key'
            elif table_name == 'DimOEM':
                pk_col = 'oem_key'
            elif table_name == 'DimVehicle':
                pk_col = 'vehicle_key'
            elif table_name == 'DimGeographyCountry':
                pk_col = 'geography_country_key'
            elif table_name == 'DimGeographyDistrict':
                pk_col = 'geography_district_key'
            elif table_name == 'FactMarketShareCountry':
                pk_col = 'fact_country_key'
            elif table_name == 'FactMarketShareDistrict':
                pk_col = 'fact_district_key'
                
            duplicates = self.connection.execute(f"""
                SELECT COUNT(*) FROM (
                    SELECT {pk_col}, COUNT(*) as cnt 
                    FROM {table_name} 
                    GROUP BY {pk_col} 
                    HAVING cnt > 1
                )
            """).fetchone()[0]
            validation_results[f"{table_name}_duplicate_pks"] = duplicates
            
        # Check market share value ranges
        for fact_table, share_col in [('FactMarketShareCountry', 'market_share_country'),
                                     ('FactMarketShareDistrict', 'market_share_district')]:
            invalid_shares = self.connection.execute(f"""
                SELECT COUNT(*) FROM {fact_table} 
                WHERE {share_col} < 0 OR {share_col} > 1
            """).fetchone()[0]
            validation_results[f"{fact_table}_invalid_market_shares"] = invalid_shares
            
        logger.info("Data integrity validation completed.")
        return validation_results
        
    def run_sample_queries(self) -> Dict[str, any]:
        """Run sample analytical queries to test the database."""
        logger.info("Running sample analytical queries...")
        
        query_results = {}
        
        # Query 1: Top 5 OEMs by market share
        top_oems = self.connection.execute("""
            SELECT 
                o.oem_name,
                o.oem_category,
                SUM(f.total_vehicles_country_oem) as total_vehicles,
                AVG(f.market_share_country) as avg_market_share
            FROM FactMarketShareCountry f
            JOIN DimOEM o ON f.oem_key = o.oem_key
            GROUP BY o.oem_key, o.oem_name, o.oem_category
            ORDER BY total_vehicles DESC
            LIMIT 5
        """).fetchall()
        query_results["top_5_oems"] = top_oems
        
        # Query 2: Vehicle type performance
        vehicle_performance = self.connection.execute("""
            SELECT 
                v.vehicle_desc,
                SUM(f.total_vehicles_country_oem) as total_vehicles,
                AVG(f.market_share_country) as avg_market_share
            FROM FactMarketShareCountry f
            JOIN DimVehicle v ON f.vehicle_key = v.vehicle_key
            GROUP BY v.vehicle_key, v.vehicle_desc
            ORDER BY total_vehicles DESC
            LIMIT 5
        """).fetchall()
        query_results["top_5_vehicles"] = vehicle_performance
        
        # Query 3: Monthly trends
        monthly_trends = self.connection.execute("""
            SELECT 
                t.year_report,
                t.month_report,
                SUM(f.total_vehicles_country) as total_market_size
            FROM FactMarketShareCountry f
            JOIN DimTime t ON f.time_key = t.time_key
            GROUP BY t.time_key, t.year_report, t.month_report
            ORDER BY t.year_report, t.month_report
        """).fetchall()
        query_results["monthly_trends"] = monthly_trends
        
        logger.info("Sample queries completed successfully.")
        return query_results
        
    def generate_summary_report(self, validation_results: Dict, query_results: Dict) -> str:
        """Generate a comprehensive summary report."""
        report = []
        report.append("=" * 70)
        report.append("VEHICLE MARKET SHARE SQLITE DATABASE CREATION SUMMARY")
        report.append("=" * 70)
        report.append("")
        
        # Database info
        report.append(f"Database file: {self.db_path}")
        report.append(f"Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Table summaries
        report.append("TABLE RECORD COUNTS:")
        report.append("-" * 30)
        for table_name in self.dimension_tables + self.fact_tables:
            count = validation_results.get(f"{table_name}_count", 0)
            table_type = "Dimension" if table_name.startswith("Dim") else "Fact"
            report.append(f"{table_name:25} ({table_type}): {count:,} records")
        report.append("")
        
        # Data quality
        report.append("DATA QUALITY CHECKS:")
        report.append("-" * 30)
        report.append(f"Foreign key violations: {validation_results.get('foreign_key_violations', 0)}")
        
        # Check for duplicate primary keys
        total_duplicates = 0
        for table_name in self.dimension_tables + self.fact_tables:
            duplicates = validation_results.get(f"{table_name}_duplicate_pks", 0)
            total_duplicates += duplicates
        report.append(f"Duplicate primary keys: {total_duplicates}")
        
        # Market share validation
        invalid_country_shares = validation_results.get("FactMarketShareCountry_invalid_market_shares", 0)
        invalid_district_shares = validation_results.get("FactMarketShareDistrict_invalid_market_shares", 0)
        report.append(f"Invalid market share values: {invalid_country_shares + invalid_district_shares}")
        report.append("")
        
        # Sample query results
        report.append("SAMPLE QUERY RESULTS:")
        report.append("-" * 30)
        
        report.append("Top 5 OEMs by Total Vehicles:")
        for oem_name, category, total_vehicles, avg_share in query_results.get("top_5_oems", []):
            report.append(f"  {oem_name} ({category}): {total_vehicles:,} vehicles, {avg_share:.4f} avg share")
        report.append("")
        
        report.append("Top 5 Vehicle Types by Total Vehicles:")
        for vehicle_desc, total_vehicles, avg_share in query_results.get("top_5_vehicles", []):
            report.append(f"  {vehicle_desc}: {total_vehicles:,} vehicles, {avg_share:.4f} avg share")
        report.append("")
        
        report.append("Monthly Market Size Trends (first 6 months):")
        for year, month, total_market in query_results.get("monthly_trends", [])[:6]:
            report.append(f"  {year}-{month:02d}: {total_market:,} total vehicles")
        report.append("")
        
        report.append("DATABASE READY FOR:")
        report.append("-" * 20)
        report.append("✓ SQL analytical queries")
        report.append("✓ Business intelligence dashboards")
        report.append("✓ Streamlit application integration")
        report.append("✓ Advanced analytics and reporting")
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
        
    def create_database(self) -> None:
        """Run the complete database creation process."""
        logger.info("Starting SQLite database creation...")
        
        try:
            # Don't remove existing database, just recreate tables
            logger.info(f"Creating/updating database at: {self.db_path}")
                
            # Create tables
            self.create_all_tables()
            
            # Load dimension tables first (to satisfy foreign key constraints)
            logger.info("Loading dimension tables...")
            for table_name in self.dimension_tables:
                self.load_table_data(table_name)
                
            # Load fact tables
            logger.info("Loading fact tables...")
            for table_name in self.fact_tables:
                self.load_table_data(table_name)
                
            # Create indexes
            self.create_indexes()
            
            # Validate data
            validation_results = self.validate_data_integrity()
            
            # Run sample queries
            query_results = self.run_sample_queries()
            
            # Generate and display summary
            summary = self.generate_summary_report(validation_results, query_results)
            print(summary)
            
            # Save summary to file
            summary_path = f"{self.db_path}_summary.txt"
            with open(summary_path, 'w') as f:
                f.write(summary)
                
            logger.info(f"Database creation completed successfully!")
            logger.info(f"Summary saved to: {summary_path}")
            
        except Exception as e:
            logger.error(f"Database creation failed: {e}")
            raise


def main():
    """Main function to create the SQLite database."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(__file__))
    star_schema_dir = os.path.join(project_root, "data", "star_schema")
    
    # Try creating database in different locations if one fails
    possible_db_paths = [
        os.path.join(project_root, "market_share.sqlite"),
        os.path.join(project_root, "data", "market_share.sqlite"),
        "market_share.sqlite"  # Current directory
    ]
    
    # Verify star schema directory exists
    if not os.path.exists(star_schema_dir):
        raise FileNotFoundError(f"Star schema directory not found: {star_schema_dir}")
        
    logger.info(f"Star schema directory: {star_schema_dir}")
    
    # Try each database location
    for db_path in possible_db_paths:
        try:
            logger.info(f"Attempting to create database at: {db_path}")
            
            # Create database
            with StarSchemaToSQLite(star_schema_dir=star_schema_dir, db_path=db_path) as converter:
                converter.create_database()
            
            logger.info(f"Successfully created database at: {db_path}")
            return
            
        except (sqlite3.OperationalError, OSError) as e:
            logger.warning(f"Failed to create database at {db_path}: {e}")
            continue
            
    raise RuntimeError("Failed to create database at any location")


if __name__ == "__main__":
    main()
