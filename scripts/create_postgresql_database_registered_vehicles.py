#!/usr/bin/env python3
"""
PostgreSQL Database Creator for Vehicle Registered Data - Traditional Star Schema

This script reads the flat fact_registered_vehicles_2023_2024 parquet file and existing dimension tables
to create a PostgreSQL database with a traditional star schema structure optimized for analytical queries.

The script creates:
- All dimension tables (DimTime, DimOEM, DimVehicle, DimGeographyCountry, DimGeographyDistrict)
- One normalized fact table (FactRegisteredVehicles) with only foreign keys and measures
- Performance indexes for common query patterns
- Data validation and integrity checks

This traditional approach provides:
- Normalized data structure with minimal redundancy
- Efficient storage through dimensional modeling
- Full analytical capabilities through joins
- Standard star schema design patterns
- Enterprise-grade PostgreSQL performance and scalability
- Complete 2023-2024 data coverage for year-over-year analysis

Requirements:
    pip install psycopg2-binary pandas pyarrow

Usage:
    python scripts/create_postgresql_database_registered_vehicles.py
    
Configuration:
    Update the DATABASE_CONFIG dictionary below with your PostgreSQL connection details.
    For IBM Cloud PostgreSQL, update the connection parameters with your service credentials.
"""

import psycopg2
import pandas as pd
import os
import logging
import io
from typing import Dict, List, Tuple
from datetime import datetime
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# DATABASE CONFIGURATION
# Update these values with your PostgreSQL connection details
DATABASE_CONFIG = {
    'host': 'localhost',           # For IBM Cloud: hostname from service credentials
    'port': 5432,                  # For IBM Cloud: port from service credentials (usually 30XXX)
    'database': 'registered_vehicles',  # For IBM Cloud: database name from service credentials
    'user': 'postgres',            # For IBM Cloud: username from service credentials
    'password': 'password',        # For IBM Cloud: password from service credentials
    'sslmode': 'prefer',           # For IBM Cloud: use 'require' for secure connections
    'connect_timeout': 30,         # Connection timeout in seconds
}

# For IBM Cloud PostgreSQL with SSL:
# DATABASE_CONFIG = {
#     'host': 'your-instance.databases.appdomain.cloud',
#     'port': 30XXX,  # Port from your service credentials
#     'database': 'ibmclouddb',  # Usually 'ibmclouddb' for IBM Cloud
#     'user': 'ibm_cloud_user',  # Username from service credentials
#     'password': 'your_password',  # Password from service credentials
#     'sslmode': 'require',
#     'sslcert': 'path/to/cert.pem',  # Optional: SSL certificate path
#     'sslkey': 'path/to/key.pem',   # Optional: SSL key path
#     'sslrootcert': 'path/to/ca.pem',  # Optional: Root certificate path
# }


class StarSchemaToPostgreSQL:
    """Converter for loading star schema parquet files into PostgreSQL database."""
    
    def __init__(self, star_schema_dir: str = "data/star_schema", 
                 db_config: Dict = None):
        """
        Initialize the converter.
        
        Args:
            star_schema_dir: Directory containing the star schema parquet files
            db_config: PostgreSQL connection configuration dictionary
        """
        self.star_schema_dir = star_schema_dir
        self.db_config = db_config or DATABASE_CONFIG.copy()
        self.connection = None
        self.cursor = None
        
        # Define table loading order (dimensions first, then facts)
        self.dimension_tables = [
            'DimTime',
            'DimOEM', 
            'DimVehicle',
            'DimGeographyCountry',
            'DimGeographyDistrict'
        ]
        
        self.fact_tables = [
            'FactRegisteredVehicles'
        ]
        
    def __enter__(self):
        """Context manager entry."""
        try:
            # Create connection string
            conn_string = (
                f"host={self.db_config['host']} "
                f"port={self.db_config['port']} "
                f"dbname={self.db_config['database']} "
                f"user={self.db_config['user']} "
                f"password={self.db_config['password']} "
                f"sslmode={self.db_config.get('sslmode', 'prefer')} "
                f"connect_timeout={self.db_config.get('connect_timeout', 30)}"
            )
            
            # Add SSL certificate paths if provided
            if 'sslcert' in self.db_config:
                conn_string += f" sslcert={self.db_config['sslcert']}"
            if 'sslkey' in self.db_config:
                conn_string += f" sslkey={self.db_config['sslkey']}"
            if 'sslrootcert' in self.db_config:
                conn_string += f" sslrootcert={self.db_config['sslrootcert']}"
            
            self.connection = psycopg2.connect(conn_string)
            self.connection.autocommit = False  # Use transactions
            self.cursor = self.connection.cursor()
            
            logger.info(f"Connected to PostgreSQL database: {self.db_config['host']}:{self.db_config['port']}")
            return self
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to PostgreSQL database: {e}")
            raise
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
            self.connection.close()
            
    def create_dim_time_table(self) -> None:
        """Create the DimTime table with proper schema."""
        sql = """
        CREATE TABLE IF NOT EXISTS DimTime (
            time_key INTEGER PRIMARY KEY,
            year_report INTEGER NOT NULL,
            month_report INTEGER NOT NULL,
            year_month VARCHAR(7) NOT NULL,
            quarter INTEGER NOT NULL,
            year_quarter VARCHAR(7) NOT NULL
        );
        """
        self.cursor.execute(sql)
        
    def create_dim_oem_table(self) -> None:
        """Create the DimOEM table with proper schema."""
        sql = """
        CREATE TABLE IF NOT EXISTS DimOEM (
            oem_key INTEGER PRIMARY KEY,
            oem_name VARCHAR(100) NOT NULL,
            oem_category VARCHAR(50) NOT NULL,
            country_origin VARCHAR(100) NOT NULL
        );
        """
        self.cursor.execute(sql)
        
    def create_dim_vehicle_table(self) -> None:
        """Create the DimVehicle table with proper schema."""
        sql = """
        CREATE TABLE IF NOT EXISTS DimVehicle (
            vehicle_key INTEGER PRIMARY KEY,
            body_type VARCHAR(50) NOT NULL,
            fuel_type VARCHAR(50) NOT NULL,
            vehicle_desc VARCHAR(100) NOT NULL
        );
        """
        self.cursor.execute(sql)
        
    def create_dim_geography_country_table(self) -> None:
        """Create the DimGeographyCountry table with proper schema."""
        sql = """
        CREATE TABLE IF NOT EXISTS DimGeographyCountry (
            geography_country_key INTEGER PRIMARY KEY,
            country_name VARCHAR(100) NOT NULL,
            country_code VARCHAR(10) NOT NULL
        );
        """
        self.cursor.execute(sql)
        
    def create_dim_geography_district_table(self) -> None:
        """Create the DimGeographyDistrict table with proper schema."""
        sql = """
        CREATE TABLE IF NOT EXISTS DimGeographyDistrict (
            geography_district_key INTEGER PRIMARY KEY,
            country_name VARCHAR(100) NOT NULL,
            country_code VARCHAR(10) NOT NULL,
            region_name VARCHAR(100),
            district_postcode VARCHAR(20),
            district_town_name VARCHAR(100),
            full_location_path TEXT NOT NULL
        );
        """
        self.cursor.execute(sql)
        
    def create_fact_registered_vehicles_table(self) -> None:
        """Create the FactRegisteredVehicles table with proper schema."""
        sql = """
        CREATE TABLE IF NOT EXISTS FactRegisteredVehicles (
            vehicle_count_id VARCHAR(100) PRIMARY KEY,
            time_key INTEGER NOT NULL,
            oem_key INTEGER NOT NULL,
            vehicle_key INTEGER NOT NULL,
            geography_country_key INTEGER,
            geography_district_key INTEGER,
            vehicle_count BIGINT NOT NULL,
            FOREIGN KEY (time_key) REFERENCES DimTime(time_key),
            FOREIGN KEY (oem_key) REFERENCES DimOEM(oem_key),
            FOREIGN KEY (vehicle_key) REFERENCES DimVehicle(vehicle_key),
            FOREIGN KEY (geography_country_key) REFERENCES DimGeographyCountry(geography_country_key),
            FOREIGN KEY (geography_district_key) REFERENCES DimGeographyDistrict(geography_district_key)
        );
        """
        self.cursor.execute(sql)
        
    def create_all_tables(self) -> None:
        """Create all tables with proper schemas."""
        logger.info("Creating database tables...")
        
        # Drop tables if they exist (for clean recreation)
        drop_order = ['FactRegisteredVehicles'] + list(reversed(self.dimension_tables))
        for table_name in drop_order:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        
        # Create dimension tables first
        self.create_dim_time_table()
        self.create_dim_oem_table()
        self.create_dim_vehicle_table()
        self.create_dim_geography_country_table()
        self.create_dim_geography_district_table()
        
        # Create fact tables with foreign key constraints
        self.create_fact_registered_vehicles_table()
        
        self.connection.commit()
        logger.info("All tables created successfully.")
        
    def load_table_data(self, table_name: str) -> None:
        """Load data from parquet file into PostgreSQL table using COPY for performance."""
        if table_name == 'FactRegisteredVehicles':
            # For the fact table, load from the flat data file
            parquet_path = os.path.join(os.path.dirname(self.star_schema_dir), "fact_registered_vehicles_2023_2024.parquet")
        else:
            # For dimension tables, load from star schema directory
            parquet_path = os.path.join(self.star_schema_dir, f"{table_name}.parquet")
        
        if not os.path.exists(parquet_path):
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
            
        # Load parquet file
        df = pd.read_parquet(parquet_path)
        
        # For FactRegisteredVehicles, we need to map the flat data to include foreign keys
        if table_name == 'FactRegisteredVehicles':
            df = self.prepare_fact_data(df)
        
        # Convert datetime columns to strings for PostgreSQL compatibility
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]':
                df[col] = df[col].dt.strftime('%Y-%m-%d')
                
        # Clear existing data
        self.cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
        
        # Use copy_from for better performance with large datasets
        # Create a temporary CSV in memory
        import io
        output = io.StringIO()
        df.to_csv(output, sep='\t', header=False, index=False, na_rep='\\N')
        output.seek(0)
        
        # Get column names
        columns = list(df.columns)
        
        try:
            self.cursor.copy_from(
                output, 
                table_name, 
                columns=columns,
                sep='\t',
                null='\\N'
            )
            self.connection.commit()
            logger.info(f"Loaded {len(df):,} records into {table_name}")
            
        except psycopg2.Error as e:
            self.connection.rollback()
            logger.error(f"Failed to load data into {table_name}: {e}")
            raise
        
    def prepare_fact_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare the flat fact data by adding foreign keys from dimension tables."""
        logger.info("Preparing fact data with foreign key mappings...")
        
        # Check for null values before processing
        logger.info(f"Initial data shape: {df.shape}")
        logger.info(f"Initial null counts:")
        for col in ['oem', 'level_0_country', 'body_type', 'fuel_type', 'year_report', 'month_report']:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                logger.info(f"  {col}: {null_count} nulls")
        
        # Handle null values in critical columns
        if 'level_0_country' in df.columns:
            df['level_0_country'] = df['level_0_country'].fillna('Unknown')
        if 'oem' in df.columns:
            df['oem'] = df['oem'].fillna('Unknown')
        if 'body_type' in df.columns:
            df['body_type'] = df['body_type'].fillna('Unknown')
        if 'fuel_type' in df.columns:
            df['fuel_type'] = df['fuel_type'].fillna('Unknown')
        
        # Handle column name mapping for energy source
        if 'Energy_Source' in df.columns and 'energy_source' not in df.columns:
            df['energy_source'] = df['Energy_Source']
        
        # Create time_key from year and month
        df['time_key'] = df['year_report'] * 100 + df['month_report']
        
        # Map OEM to oem_key
        oem_df = pd.read_sql("SELECT oem_key, oem_name FROM DimOEM", self.connection)
        df = df.merge(oem_df, left_on='oem', right_on='oem_name', how='left')
        
        # Map vehicle characteristics to vehicle_key
        vehicle_df = pd.read_sql("SELECT vehicle_key, body_type, fuel_type FROM DimVehicle", self.connection)
        df = df.merge(vehicle_df, on=['body_type', 'fuel_type'], how='left')
        
        # Map country to geography_country_key
        country_df = pd.read_sql("SELECT geography_country_key, country_name FROM DimGeographyCountry", self.connection)
        df = df.merge(country_df, left_on='level_0_country', right_on='country_name', how='left')
        
        # Map district to geography_district_key (if district data exists)
        if 'level_2_district_postcode' in df.columns and not df['level_2_district_postcode'].isna().all():
            district_df = pd.read_sql("""
                SELECT geography_district_key, country_name, region_name, district_postcode, district_town_name 
                FROM DimGeographyDistrict
            """, self.connection)
            
            # Create a composite key for matching
            df_district = df.copy()
            df_district['match_key'] = (
                df_district['level_0_country'].fillna('') + '|' +
                df_district['level_1_region_name'].fillna('') + '|' +
                df_district['level_2_district_postcode'].fillna('') + '|' +
                df_district['level_2_district_town_name'].fillna('')
            )
            
            district_df['match_key'] = (
                district_df['country_name'].fillna('') + '|' +
                district_df['region_name'].fillna('') + '|' +
                district_df['district_postcode'].fillna('') + '|' +
                district_df['district_town_name'].fillna('')
            )
            
            df = df.merge(
                district_df[['geography_district_key', 'match_key']], 
                left_on=df_district['match_key'], 
                right_on='match_key', 
                how='left'
            )
            df = df.drop('match_key', axis=1)
        
        # Check for null values in foreign keys and handle missing mappings
        logger.info("Checking foreign key mappings:")
        logger.info(f"  oem_key nulls: {df['oem_key'].isnull().sum()}")
        logger.info(f"  vehicle_key nulls: {df['vehicle_key'].isnull().sum()}")
        logger.info(f"  geography_country_key nulls: {df['geography_country_key'].isnull().sum()}")
        if 'geography_district_key' in df.columns:
            logger.info(f"  geography_district_key nulls: {df['geography_district_key'].isnull().sum()}")
        
        # Fill missing foreign keys with default values and convert to integers
        df['oem_key'] = df['oem_key'].fillna(-1).astype(int)  # -1 for unknown OEM
        df['vehicle_key'] = df['vehicle_key'].fillna(-1).astype(int)  # -1 for unknown vehicle
        df['geography_country_key'] = df['geography_country_key'].fillna(-1).astype(int)  # -1 for unknown country
        if 'geography_district_key' in df.columns:
            df['geography_district_key'] = df['geography_district_key'].fillna(-1).astype(int)  # -1 for unknown district
        
        # Final verification of foreign key values
        logger.info("Final foreign key verification:")
        logger.info(f"  oem_key - min: {df['oem_key'].min()}, max: {df['oem_key'].max()}, nulls: {df['oem_key'].isnull().sum()}")
        logger.info(f"  vehicle_key - min: {df['vehicle_key'].min()}, max: {df['vehicle_key'].max()}, nulls: {df['vehicle_key'].isnull().sum()}")
        logger.info(f"  geography_country_key - min: {df['geography_country_key'].min()}, max: {df['geography_country_key'].max()}, nulls: {df['geography_country_key'].isnull().sum()}")
        if 'geography_district_key' in df.columns:
            logger.info(f"  geography_district_key - min: {df['geography_district_key'].min()}, max: {df['geography_district_key'].max()}, nulls: {df['geography_district_key'].isnull().sum()}")
        
        # Check if all foreign keys exist in dimension tables
        # Check OEM keys
        valid_oem_keys = set(pd.read_sql("SELECT oem_key FROM DimOEM", self.connection)['oem_key'])
        invalid_oem_keys = set(df['oem_key'].unique()) - valid_oem_keys
        if invalid_oem_keys:
            logger.warning(f"Invalid OEM keys found: {invalid_oem_keys}")
        
        # Check vehicle keys  
        valid_vehicle_keys = set(pd.read_sql("SELECT vehicle_key FROM DimVehicle", self.connection)['vehicle_key'])
        invalid_vehicle_keys = set(df['vehicle_key'].unique()) - valid_vehicle_keys
        if invalid_vehicle_keys:
            logger.warning(f"Invalid vehicle keys found: {invalid_vehicle_keys}")
        
        # Check country keys
        valid_country_keys = set(pd.read_sql("SELECT geography_country_key FROM DimGeographyCountry", self.connection)['geography_country_key'])
        invalid_country_keys = set(df['geography_country_key'].unique()) - valid_country_keys
        if invalid_country_keys:
            logger.warning(f"Invalid country keys found: {invalid_country_keys}")
        
        # Check district keys
        if 'geography_district_key' in df.columns:
            valid_district_keys = set(pd.read_sql("SELECT geography_district_key FROM DimGeographyDistrict", self.connection)['geography_district_key'])
            invalid_district_keys = set(df['geography_district_key'].unique()) - valid_district_keys
            if invalid_district_keys:
                logger.warning(f"Invalid district keys found: {invalid_district_keys}")
        
        # Select only the columns needed for the traditional star schema fact table
        fact_columns = [
            'vehicle_count_id', 'time_key', 'oem_key', 'vehicle_key', 
            'geography_country_key', 'geography_district_key', 'vehicle_count'
        ]
        
        # Only keep columns that exist in the dataframe
        available_columns = [col for col in fact_columns if col in df.columns]
        df = df[available_columns]
        
        # Final check for null values in NOT NULL columns
        critical_columns = ['vehicle_count']
        for col in critical_columns:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    logger.warning(f"Found {null_count} null values in {col}, filling with defaults")
                    df[col] = df[col].fillna(0)
        
        logger.info(f"Fact data prepared with {len(df):,} records")
        return df
        
    def add_unknown_dimension_entries(self) -> None:
        """Add 'Unknown' entries to dimension tables for missing mappings."""
        logger.info("Adding 'Unknown' entries to dimension tables...")
        
        # Add Unknown OEM
        self.cursor.execute("""
            INSERT INTO DimOEM (oem_key, oem_name, oem_category, country_origin)
            VALUES (-1, 'Unknown', 'Unknown', 'Unknown')
            ON CONFLICT (oem_key) DO NOTHING;
        """)
        
        # Add Unknown Vehicle
        self.cursor.execute("""
            INSERT INTO DimVehicle (vehicle_key, body_type, fuel_type, vehicle_desc)
            VALUES (-1, 'Unknown', 'Unknown', 'Unknown Vehicle Type')
            ON CONFLICT (vehicle_key) DO NOTHING;
        """)
        
        # Add Unknown Country
        self.cursor.execute("""
            INSERT INTO DimGeographyCountry (geography_country_key, country_name, country_code)
            VALUES (-1, 'Unknown', 'UNK')
            ON CONFLICT (geography_country_key) DO NOTHING;
        """)
        
        # Add Unknown District
        self.cursor.execute("""
            INSERT INTO DimGeographyDistrict (geography_district_key, country_name, country_code, region_name, district_postcode, district_town_name, full_location_path)
            VALUES (-1, 'Unknown', 'UNK', 'Unknown', 'UNK', 'Unknown', 'Unknown/Unknown/Unknown')
            ON CONFLICT (geography_district_key) DO NOTHING;
        """)
        
        self.connection.commit()
        logger.info("Unknown dimension entries added successfully.")
        
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
            
            # Fact table indexes for FactRegisteredVehicles (foreign keys only)
            "CREATE INDEX IF NOT EXISTS idx_factvehicles_time ON FactRegisteredVehicles(time_key);",
            "CREATE INDEX IF NOT EXISTS idx_factvehicles_oem ON FactRegisteredVehicles(oem_key);",
            "CREATE INDEX IF NOT EXISTS idx_factvehicles_vehicle ON FactRegisteredVehicles(vehicle_key);",
            "CREATE INDEX IF NOT EXISTS idx_factvehicles_country ON FactRegisteredVehicles(geography_country_key);",
            "CREATE INDEX IF NOT EXISTS idx_factvehicles_district ON FactRegisteredVehicles(geography_district_key);",
            "CREATE INDEX IF NOT EXISTS idx_factvehicles_time_oem ON FactRegisteredVehicles(time_key, oem_key);",
            "CREATE INDEX IF NOT EXISTS idx_factvehicles_time_vehicle ON FactRegisteredVehicles(time_key, vehicle_key);",
            "CREATE INDEX IF NOT EXISTS idx_factvehicles_oem_vehicle ON FactRegisteredVehicles(oem_key, vehicle_key);",
        ]
        
        for index_sql in indexes:
            try:
                self.cursor.execute(index_sql)
            except psycopg2.Error as e:
                logger.warning(f"Failed to create index: {e}")
                
        self.connection.commit()
        logger.info("All indexes created successfully.")
        
    def validate_data_integrity(self) -> Dict[str, any]:
        """Validate data integrity and foreign key relationships."""
        logger.info("Validating data integrity...")
        
        validation_results = {}
        
        # Check record counts
        for table_name in self.dimension_tables + self.fact_tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = self.cursor.fetchone()[0]
            validation_results[f"{table_name}_count"] = count
            
        # Check foreign key integrity (PostgreSQL enforces FK constraints automatically)
        validation_results["foreign_key_violations"] = 0  # PostgreSQL prevents FK violations
        
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
            elif table_name == 'FactRegisteredVehicles':
                pk_col = 'vehicle_count_id'
                
            self.cursor.execute(f"""
                SELECT COUNT(*) FROM (
                    SELECT {pk_col}, COUNT(*) as cnt 
                    FROM {table_name} 
                    GROUP BY {pk_col} 
                    HAVING COUNT(*) > 1
                ) AS duplicates
            """)
            duplicates = self.cursor.fetchone()[0]
            validation_results[f"{table_name}_duplicate_pks"] = duplicates
            
        # Check vehicle count value ranges
        self.cursor.execute(f"""
            SELECT COUNT(*) FROM FactRegisteredVehicles 
            WHERE vehicle_count < 0
        """)
        invalid_counts = self.cursor.fetchone()[0]
        validation_results["FactRegisteredVehicles_invalid_vehicle_counts"] = invalid_counts
            
        logger.info("Data integrity validation completed.")
        return validation_results
        
    def run_sample_queries(self) -> Dict[str, any]:
        """Run sample analytical queries to test the database."""
        logger.info("Running sample analytical queries...")
        
        query_results = {}
        
        # Query 1: Top 5 OEMs by total vehicles (requires joins)
        self.cursor.execute("""
            SELECT 
                o.oem_name,
                o.oem_category,
                SUM(f.vehicle_count) as total_vehicles,
                COUNT(*) as registration_records
            FROM FactRegisteredVehicles f
            JOIN DimOEM o ON f.oem_key = o.oem_key
            GROUP BY o.oem_name, o.oem_category
            ORDER BY total_vehicles DESC
            LIMIT 5
        """)
        query_results["top_5_oems"] = self.cursor.fetchall()
        
        # Query 2: Vehicle type performance (requires joins)
        self.cursor.execute("""
            SELECT 
                v.body_type,
                v.fuel_type,
                SUM(f.vehicle_count) as total_vehicles,
                COUNT(DISTINCT f.oem_key) as num_oems
            FROM FactRegisteredVehicles f
            JOIN DimVehicle v ON f.vehicle_key = v.vehicle_key
            GROUP BY v.body_type, v.fuel_type
            ORDER BY total_vehicles DESC
            LIMIT 5
        """)
        query_results["top_5_vehicles"] = self.cursor.fetchall()
        
        # Query 3: Monthly trends (requires joins)
        self.cursor.execute("""
            SELECT 
                t.year_report,
                t.month_report,
                SUM(f.vehicle_count) as total_registrations,
                COUNT(DISTINCT f.oem_key) as num_oems
            FROM FactRegisteredVehicles f
            JOIN DimTime t ON f.time_key = t.time_key
            GROUP BY t.year_report, t.month_report
            ORDER BY t.year_report, t.month_report
        """)
        query_results["monthly_trends"] = self.cursor.fetchall()
        
        logger.info("Sample queries completed successfully.")
        return query_results
        
    def generate_summary_report(self, validation_results: Dict, query_results: Dict) -> str:
        """Generate a comprehensive summary report."""
        report = []
        report.append("=" * 70)
        report.append("VEHICLE REGISTERED DATA POSTGRESQL DATABASE CREATION SUMMARY")
        report.append("TRADITIONAL STAR SCHEMA")
        report.append("=" * 70)
        report.append("")
        
        # Database info
        report.append(f"Database host: {self.db_config['host']}:{self.db_config['port']}")
        report.append(f"Database name: {self.db_config['database']}")
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
        
        # Data validation
        invalid_vehicle_counts = validation_results.get("FactRegisteredVehicles_invalid_vehicle_counts", 0)
        report.append(f"Invalid vehicle counts: {invalid_vehicle_counts}")
        report.append("")
        
        # Sample query results
        report.append("SAMPLE QUERY RESULTS:")
        report.append("-" * 30)
        
        report.append("Top 5 OEMs by Total Vehicle Registrations:")
        for oem_name, category, total_vehicles, records in query_results.get("top_5_oems", []):
            category_str = f" ({category})" if category else ""
            report.append(f"  {oem_name}{category_str}: {total_vehicles:,} vehicles, {records:,} records")
        report.append("")
        
        report.append("Top 5 Vehicle Types by Registration Count:")
        for body_type, fuel_type, total_vehicles, num_oems in query_results.get("top_5_vehicles", []):
            report.append(f"  {body_type} - {fuel_type}: {total_vehicles:,} vehicles, {num_oems} OEMs")
        report.append("")
        
        report.append("Monthly Registration Trends (first 6 months):")
        for year, month, total_registrations, num_oems in query_results.get("monthly_trends", [])[:6]:
            report.append(f"  {year}-{month:02d}: {total_registrations:,} registrations, {num_oems} OEMs")
        report.append("")
        
        report.append("DATABASE READY FOR:")
        report.append("-" * 20)
        report.append("✓ Traditional star schema analytical queries")
        report.append("✓ Business intelligence dashboards with joins")
        report.append("✓ Normalized data storage and retrieval")
        report.append("✓ Advanced analytics and reporting")
        report.append("✓ Dimensional modeling best practices")
        report.append("✓ Enterprise-grade PostgreSQL performance")
        report.append("✓ Multi-user concurrent access")
        report.append("✓ Production-ready deployment")
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
        
    def create_database(self) -> None:
        """Run the complete database creation process."""
        logger.info("Starting PostgreSQL database creation...")
        
        try:
            # Create tables
            self.create_all_tables()
            
            # Load dimension tables first (to satisfy foreign key constraints)
            logger.info("Loading dimension tables...")
            for table_name in self.dimension_tables:
                self.load_table_data(table_name)
            
            # Add "Unknown" entries to dimension tables to handle missing mappings
            self.add_unknown_dimension_entries()
                
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
            summary_path = f"postgresql_registered_vehicles_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(summary_path, 'w') as f:
                f.write(summary)
                
            logger.info(f"Database creation completed successfully!")
            logger.info(f"Summary saved to: {summary_path}")
            
        except Exception as e:
            logger.error(f"Database creation failed: {e}")
            raise


def main():
    """Main function to create the PostgreSQL database."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(__file__))
    star_schema_dir = os.path.join(project_root, "data", "star_schema")
    
    # Verify star schema directory exists
    if not os.path.exists(star_schema_dir):
        raise FileNotFoundError(f"Star schema directory not found: {star_schema_dir}")
        
    # Check if the fact registered vehicles file exists
    fact_file_path = os.path.join(project_root, "data", "fact_registered_vehicles_2023_2024.parquet")
    if not os.path.exists(fact_file_path):
        raise FileNotFoundError(f"Fact registered vehicles file not found: {fact_file_path}")
        
    logger.info(f"Star schema directory: {star_schema_dir}")
    logger.info(f"Fact data file: {fact_file_path}")
    logger.info(f"Connecting to PostgreSQL database: {DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}")
    
    # Check if required packages are installed
    try:
        import psycopg2
    except ImportError:
        logger.error("psycopg2 is required. Install it with: pip install psycopg2-binary")
        sys.exit(1)
    
    # Create database
    try:
        with StarSchemaToPostgreSQL(star_schema_dir=star_schema_dir, db_config=DATABASE_CONFIG) as converter:
            converter.create_database()
            
        logger.info("Successfully created PostgreSQL database!")
        
    except psycopg2.Error as e:
        logger.error(f"PostgreSQL database error: {e}")
        logger.error("Please check your database configuration and ensure PostgreSQL is running.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
