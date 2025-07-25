#!/usr/bin/env python3
"""
Vehicle Market Share Star Schema ETL

This script reads the fact_market_share_country and fact_market_share_district 
parquet files and creates dimension tables for a star schema design.

The script generates:
- DimTime: Time dimension with temporal attributes
- DimOEM: Original Equipment Manufacturer dimension with categories
- DimVehicle: Vehicle characteristics dimension
- DimGeographyCountry: Country-level geography dimension
- DimGeographyDistrict: District-level geography dimension
- FactMarketShareCountry: Transformed country-level fact table
- FactMarketShareDistrict: Transformed district-level fact table

All output files are saved as parquet format for efficient storage and querying.

Usage:
    python scripts/create_star_schema.py
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VehicleMarketStarSchemaETL:
    """ETL processor for creating vehicle market share star schema."""
    
    def __init__(self, data_dir: str = "data", output_dir: str = "data/star_schema"):
        """
        Initialize the ETL processor.
        
        Args:
            data_dir: Directory containing input parquet files
            output_dir: Directory to save output parquet files
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # OEM categorization mappings
        self.oem_categories = {
            # Luxury brands
            'MERCEDES-BENZ': ('Luxury', 'Germany'),
            'BMW': ('Luxury', 'Germany'),
            'AUDI': ('Luxury', 'Germany'),
            'PORSCHE': ('Luxury', 'Germany'),
            'JAGUAR': ('Luxury', 'UK'),
            'LAND ROVER': ('Luxury', 'UK'),
            'BENTLEY': ('Luxury', 'UK'),
            'ROLLS-ROYCE': ('Luxury', 'UK'),
            'FERRARI': ('Luxury', 'Italy'),
            'LAMBORGHINI': ('Luxury', 'Italy'),
            'MASERATI': ('Luxury', 'Italy'),
            'ASTON MARTIN': ('Luxury', 'UK'),
            
            # Premium brands
            'VOLVO': ('Premium', 'Sweden'),
            'LEXUS': ('Premium', 'Japan'),
            'INFINITI': ('Premium', 'Japan'),
            'ACURA': ('Premium', 'Japan'),
            'GENESIS': ('Premium', 'South Korea'),
            'CADILLAC': ('Premium', 'USA'),
            'LINCOLN': ('Premium', 'USA'),
            'TESLA': ('Premium', 'USA'),
            
            # German mass market
            'VOLKSWAGEN': ('Mass Market', 'Germany'),
            'OPEL': ('Mass Market', 'Germany'),
            'FORD': ('Mass Market', 'Germany'),  # Ford Europe
            
            # Japanese mass market
            'TOYOTA': ('Mass Market', 'Japan'),
            'HONDA': ('Mass Market', 'Japan'),
            'NISSAN': ('Mass Market', 'Japan'),
            'MAZDA': ('Mass Market', 'Japan'),
            'SUBARU': ('Mass Market', 'Japan'),
            'MITSUBISHI': ('Mass Market', 'Japan'),
            'SUZUKI': ('Mass Market', 'Japan'),
            'ISUZU': ('Mass Market', 'Japan'),
            
            # American mass market
            'CHEVROLET': ('Mass Market', 'USA'),
            'BUICK': ('Mass Market', 'USA'),
            'GMC': ('Mass Market', 'USA'),
            'CHRYSLER': ('Mass Market', 'USA'),
            'DODGE': ('Mass Market', 'USA'),
            'JEEP': ('Mass Market', 'USA'),
            
            # Korean mass market
            'HYUNDAI': ('Mass Market', 'South Korea'),
            'KIA': ('Mass Market', 'South Korea'),
            
            # French mass market
            'PEUGEOT': ('Mass Market', 'France'),
            'CITROËN': ('Mass Market', 'France'),
            'RENAULT': ('Mass Market', 'France'),
            
            # Italian mass market
            'FIAT': ('Mass Market', 'Italy'),
            'ALFA ROMEO': ('Mass Market', 'Italy'),
            
            # Other European
            'SEAT': ('Mass Market', 'Spain'),
            'SKODA': ('Mass Market', 'Czech Republic'),
            'DACIA': ('Mass Market', 'Romania'),
        }
        
        # Country code mappings
        self.country_codes = {
            'England': 'GBR',
            'Scotland': 'GBR',
            'Wales': 'GBR',
            'Northern Ireland': 'GBR',
            'Germany': 'DEU',
            'France': 'FRA',
            'Italy': 'ITA',
            'Spain': 'ESP',
            'Netherlands': 'NLD',
            'Belgium': 'BEL',
            'Austria': 'AUT',
            'Switzerland': 'CHE',
            'Sweden': 'SWE',
            'Norway': 'NOR',
            'Denmark': 'DNK',
            'Finland': 'FIN',
            'Poland': 'POL',
            'Czech Republic': 'CZE',
            'Hungary': 'HUN',
            'Romania': 'ROU',
            'Bulgaria': 'BGR',
            'Greece': 'GRC',
            'Portugal': 'PRT',
            'Ireland': 'IRL',
            'Luxembourg': 'LUX',
            'Malta': 'MLT',
            'Cyprus': 'CYP',
            'Slovenia': 'SVN',
            'Slovakia': 'SVK',
            'Estonia': 'EST',
            'Latvia': 'LVA',
            'Lithuania': 'LTU',
        }
        
    def load_fact_tables(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load the input fact tables from parquet files."""
        logger.info("Loading fact tables...")
        
        country_path = os.path.join(self.data_dir, "fact_market_share_country.parquet")
        district_path = os.path.join(self.data_dir, "fact_market_share_district.parquet")
        
        if not os.path.exists(country_path):
            raise FileNotFoundError(f"Country fact table not found: {country_path}")
        if not os.path.exists(district_path):
            raise FileNotFoundError(f"District fact table not found: {district_path}")
            
        fact_country = pd.read_parquet(country_path)
        fact_district = pd.read_parquet(district_path)
        
        logger.info(f"Loaded country fact table: {len(fact_country):,} records")
        logger.info(f"Loaded district fact table: {len(fact_district):,} records")
        
        return fact_country, fact_district
        
    def create_dim_time(self, fact_country: pd.DataFrame, fact_district: pd.DataFrame) -> pd.DataFrame:
        """Create the time dimension table."""
        logger.info("Creating DimTime...")
        
        # Combine time data from both fact tables
        time_data = []
        
        for df in [fact_country, fact_district]:
            time_subset = df[['year_report', 'month_report']].drop_duplicates()
            time_data.append(time_subset)
            
        combined_time = pd.concat(time_data).drop_duplicates().reset_index(drop=True)
        
        # Create time dimension
        dim_time = combined_time.copy()
        
        # Create time_key (YYYYMM format)
        dim_time['time_key'] = (dim_time['year_report'] * 100 + dim_time['month_report']).astype(int)
        
        # Create year_month date
        dim_time['year_month'] = pd.to_datetime(
            dim_time['year_report'].astype(str) + '-' + dim_time['month_report'].astype(str) + '-01'
        )
        
        # Calculate quarter
        dim_time['quarter'] = ((dim_time['month_report'] - 1) // 3 + 1).astype(int)
        
        # Create year_quarter
        dim_time['year_quarter'] = dim_time['year_report'].astype(str) + '-Q' + dim_time['quarter'].astype(str)
        
        # Reorder columns
        dim_time = dim_time[['time_key', 'year_report', 'month_report', 'year_month', 'quarter', 'year_quarter']]
        
        logger.info(f"Created DimTime with {len(dim_time)} records")
        return dim_time
        
    def create_dim_oem(self, fact_country: pd.DataFrame, fact_district: pd.DataFrame) -> pd.DataFrame:
        """Create the OEM dimension table."""
        logger.info("Creating DimOEM...")
        
        # Get unique OEMs from both fact tables
        oems = pd.concat([
            fact_country['oem'],
            fact_district['oem']
        ]).unique()
        
        # Create OEM dimension
        dim_oem_data = []
        for i, oem in enumerate(sorted(oems), 1):
            category, country_origin = self.oem_categories.get(oem, ('Mass Market', 'Unknown'))
            dim_oem_data.append({
                'oem_key': i,
                'oem_name': oem,
                'oem_category': category,
                'country_origin': country_origin
            })
            
        dim_oem = pd.DataFrame(dim_oem_data)
        
        logger.info(f"Created DimOEM with {len(dim_oem)} records")
        return dim_oem
        
    def create_dim_vehicle(self, fact_country: pd.DataFrame, fact_district: pd.DataFrame) -> pd.DataFrame:
        """Create the vehicle dimension table."""
        logger.info("Creating DimVehicle...")
        
        # Get unique vehicle combinations from both fact tables
        vehicle_combinations = []
        
        for df in [fact_country, fact_district]:
            vehicle_subset = df[['body_type', 'fuel_type']].drop_duplicates()
            vehicle_combinations.append(vehicle_subset)
            
        combined_vehicles = pd.concat(vehicle_combinations).drop_duplicates().reset_index(drop=True)
        
        # Create vehicle dimension
        dim_vehicle = combined_vehicles.copy()
        dim_vehicle['vehicle_key'] = range(1, len(dim_vehicle) + 1)
        
        # Create vehicle description
        dim_vehicle['vehicle_desc'] = dim_vehicle['body_type'] + ' - ' + dim_vehicle['fuel_type']
        
        # Reorder columns
        dim_vehicle = dim_vehicle[['vehicle_key', 'body_type', 'fuel_type', 'vehicle_desc']]
        
        logger.info(f"Created DimVehicle with {len(dim_vehicle)} records")
        return dim_vehicle
        
    def create_dim_geography_country(self, fact_country: pd.DataFrame) -> pd.DataFrame:
        """Create the country geography dimension table."""
        logger.info("Creating DimGeographyCountry...")
        
        # Get unique countries, filtering out null values
        countries = fact_country['level_0_country'].dropna().unique()
        
        # Create country dimension
        dim_geo_country_data = []
        for i, country in enumerate(sorted(countries), 1):
            country_code = self.country_codes.get(country, 'UNK')
            dim_geo_country_data.append({
                'geography_country_key': i,
                'country_name': country,
                'country_code': country_code
            })
            
        dim_geo_country = pd.DataFrame(dim_geo_country_data)
        
        logger.info(f"Created DimGeographyCountry with {len(dim_geo_country)} records")
        return dim_geo_country
        
    def create_dim_geography_district(self, fact_district: pd.DataFrame) -> pd.DataFrame:
        """Create the district geography dimension table."""
        logger.info("Creating DimGeographyDistrict...")
        
        # Get unique geographic combinations, handling null values
        geo_columns = ['level_0_country', 'level_1_region_name', 'level_2_district_postcode', 'level_2_district_town_name']
        unique_districts = fact_district[geo_columns].drop_duplicates().reset_index(drop=True)
        
        # Fill null values with 'N/A' for consistent handling
        unique_districts = unique_districts.fillna('N/A')
        
        # Create district dimension
        dim_geo_district = unique_districts.copy()
        dim_geo_district['geography_district_key'] = range(1, len(dim_geo_district) + 1)
        
        # Rename columns to match schema
        dim_geo_district = dim_geo_district.rename(columns={
            'level_0_country': 'country_name',
            'level_1_region_name': 'region_name',
            'level_2_district_postcode': 'district_postcode',
            'level_2_district_town_name': 'district_town_name'
        })
        
        # Add country codes
        dim_geo_district['country_code'] = dim_geo_district['country_name'].map(
            lambda x: self.country_codes.get(x, 'UNK')
        )
        
        # Create full location path
        def create_location_path(row):
            parts = [row['country_name']]
            if pd.notna(row['region_name']) and row['region_name'] != 'N/A':
                parts.append(row['region_name'])
            if pd.notna(row['district_town_name']) and row['district_town_name'] != 'N/A':
                parts.append(row['district_town_name'])
            if pd.notna(row['district_postcode']) and row['district_postcode'] != 'N/A':
                parts.append(f"({row['district_postcode']})")
            return ' / '.join(parts)
            
        dim_geo_district['full_location_path'] = dim_geo_district.apply(create_location_path, axis=1)
        
        # Reorder columns
        columns_order = ['geography_district_key', 'country_name', 'country_code', 'region_name', 
                        'district_postcode', 'district_town_name', 'full_location_path']
        dim_geo_district = dim_geo_district[columns_order]
        
        logger.info(f"Created DimGeographyDistrict with {len(dim_geo_district)} records")
        return dim_geo_district
        
    def create_fact_market_share_country(self, fact_country: pd.DataFrame, dim_time: pd.DataFrame, 
                                       dim_oem: pd.DataFrame, dim_vehicle: pd.DataFrame, 
                                       dim_geo_country: pd.DataFrame) -> pd.DataFrame:
        """Create the transformed country fact table."""
        logger.info("Creating FactMarketShareCountry...")
        
        # Start with original fact table
        new_fact = fact_country.copy()
        
        # Create lookup dictionaries for faster merging
        time_lookup = dict(zip(
            dim_time['year_report'] * 100 + dim_time['month_report'], 
            dim_time['time_key']
        ))
        
        oem_lookup = dict(zip(dim_oem['oem_name'], dim_oem['oem_key']))
        
        vehicle_lookup = {}
        for _, row in dim_vehicle.iterrows():
            key = (row['body_type'], row['fuel_type'])
            vehicle_lookup[key] = row['vehicle_key']
            
        geo_lookup = dict(zip(dim_geo_country['country_name'], dim_geo_country['geography_country_key']))
        
        # Map foreign keys
        new_fact['time_key'] = (new_fact['year_report'] * 100 + new_fact['month_report']).map(time_lookup)
        new_fact['oem_key'] = new_fact['oem'].map(oem_lookup)
        new_fact['vehicle_key'] = new_fact[['body_type', 'fuel_type']].apply(
            lambda x: vehicle_lookup.get((x['body_type'], x['fuel_type'])), axis=1
        )
        new_fact['geography_country_key'] = new_fact['level_0_country'].map(geo_lookup)
        
        # Create fact key
        new_fact['fact_country_key'] = range(1, len(new_fact) + 1)
        
        # Select final columns
        final_columns = [
            'fact_country_key', 'time_key', 'oem_key', 'vehicle_key', 'geography_country_key',
            'total_vehicles_country', 'total_vehicles_country_oem', 'market_share_country'
        ]
        
        new_fact = new_fact[final_columns]
        
        # Remove any rows with missing keys
        initial_count = len(new_fact)
        new_fact = new_fact.dropna(subset=['time_key', 'oem_key', 'vehicle_key', 'geography_country_key'])
        final_count = len(new_fact)
        
        if initial_count != final_count:
            logger.warning(f"Dropped {initial_count - final_count} rows due to missing foreign keys")
            
        logger.info(f"Created FactMarketShareCountry with {len(new_fact)} records")
        return new_fact
        
    def create_fact_market_share_district(self, fact_district: pd.DataFrame, dim_time: pd.DataFrame, 
                                        dim_oem: pd.DataFrame, dim_vehicle: pd.DataFrame, 
                                        dim_geo_district: pd.DataFrame) -> pd.DataFrame:
        """Create the transformed district fact table."""
        logger.info("Creating FactMarketShareDistrict...")
        
        # Start with original fact table
        new_fact = fact_district.copy()
        
        # Create lookup dictionaries
        time_lookup = dict(zip(
            dim_time['year_report'] * 100 + dim_time['month_report'], 
            dim_time['time_key']
        ))
        
        oem_lookup = dict(zip(dim_oem['oem_name'], dim_oem['oem_key']))
        
        vehicle_lookup = {}
        for _, row in dim_vehicle.iterrows():
            key = (row['body_type'], row['fuel_type'])
            vehicle_lookup[key] = row['vehicle_key']
            
        # Create geography lookup for district
        geo_lookup = {}
        for _, row in dim_geo_district.iterrows():
            key = (
                row['country_name'], 
                row['region_name'], 
                row['district_postcode'], 
                row['district_town_name']
            )
            geo_lookup[key] = row['geography_district_key']
        
        # Map foreign keys
        new_fact['time_key'] = (new_fact['year_report'] * 100 + new_fact['month_report']).map(time_lookup)
        new_fact['oem_key'] = new_fact['oem'].map(oem_lookup)
        new_fact['vehicle_key'] = new_fact[['body_type', 'fuel_type']].apply(
            lambda x: vehicle_lookup.get((x['body_type'], x['fuel_type'])), axis=1
        )
        new_fact['geography_district_key'] = new_fact[[
            'level_0_country', 'level_1_region_name', 'level_2_district_postcode', 'level_2_district_town_name'
        ]].apply(lambda x: geo_lookup.get(tuple(x)), axis=1)
        
        # Create fact key
        new_fact['fact_district_key'] = range(1, len(new_fact) + 1)
        
        # Select final columns
        final_columns = [
            'fact_district_key', 'time_key', 'oem_key', 'vehicle_key', 'geography_district_key',
            'total_vehicles_district', 'total_vehicles_district_oem', 'market_share_district'
        ]
        
        new_fact = new_fact[final_columns]
        
        # Remove any rows with missing keys
        initial_count = len(new_fact)
        new_fact = new_fact.dropna(subset=['time_key', 'oem_key', 'vehicle_key', 'geography_district_key'])
        final_count = len(new_fact)
        
        if initial_count != final_count:
            logger.warning(f"Dropped {initial_count - final_count} rows due to missing foreign keys")
            
        logger.info(f"Created FactMarketShareDistrict with {len(new_fact)} records")
        return new_fact
        
    def save_tables(self, tables: Dict[str, pd.DataFrame]) -> None:
        """Save all tables to parquet files."""
        logger.info("Saving tables to parquet files...")
        
        for table_name, df in tables.items():
            output_path = os.path.join(self.output_dir, f"{table_name}.parquet")
            df.to_parquet(output_path, index=False)
            logger.info(f"Saved {table_name}: {len(df):,} records to {output_path}")
            
    def generate_summary_report(self, tables: Dict[str, pd.DataFrame]) -> str:
        """Generate a summary report of the ETL process."""
        report = []
        report.append("=" * 60)
        report.append("VEHICLE MARKET SHARE STAR SCHEMA ETL SUMMARY")
        report.append("=" * 60)
        report.append("")
        
        # Table summaries
        for table_name, df in tables.items():
            report.append(f"{table_name}:")
            report.append(f"  Records: {len(df):,}")
            report.append(f"  Columns: {', '.join(df.columns.tolist())}")
            report.append("")
            
        # Data quality checks
        report.append("DATA QUALITY CHECKS:")
        report.append("=" * 30)
        
        # Check for null values in key columns
        if 'FactMarketShareCountry' in tables:
            fact_country = tables['FactMarketShareCountry']
            null_keys = fact_country[['time_key', 'oem_key', 'vehicle_key', 'geography_country_key']].isnull().sum()
            report.append(f"FactMarketShareCountry - NULL foreign keys: {null_keys.sum()}")
            
        if 'FactMarketShareDistrict' in tables:
            fact_district = tables['FactMarketShareDistrict']
            null_keys = fact_district[['time_key', 'oem_key', 'vehicle_key', 'geography_district_key']].isnull().sum()
            report.append(f"FactMarketShareDistrict - NULL foreign keys: {null_keys.sum()}")
            
        report.append("")
        report.append(f"ETL completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        return "\n".join(report)
        
    def run_etl(self) -> None:
        """Run the complete ETL process."""
        logger.info("Starting Vehicle Market Share Star Schema ETL...")
        
        try:
            # Load input data
            fact_country, fact_district = self.load_fact_tables()
            
            # Create dimension tables
            dim_time = self.create_dim_time(fact_country, fact_district)
            dim_oem = self.create_dim_oem(fact_country, fact_district)
            dim_vehicle = self.create_dim_vehicle(fact_country, fact_district)
            dim_geo_country = self.create_dim_geography_country(fact_country)
            dim_geo_district = self.create_dim_geography_district(fact_district)
            
            # Create fact tables
            new_fact_country = self.create_fact_market_share_country(
                fact_country, dim_time, dim_oem, dim_vehicle, dim_geo_country
            )
            new_fact_district = self.create_fact_market_share_district(
                fact_district, dim_time, dim_oem, dim_vehicle, dim_geo_district
            )
            
            # Collect all tables
            tables = {
                'DimTime': dim_time,
                'DimOEM': dim_oem,
                'DimVehicle': dim_vehicle,
                'DimGeographyCountry': dim_geo_country,
                'DimGeographyDistrict': dim_geo_district,
                'FactMarketShareCountry': new_fact_country,
                'FactMarketShareDistrict': new_fact_district
            }
            
            # Save all tables
            self.save_tables(tables)
            
            # Generate and print summary
            summary = self.generate_summary_report(tables)
            print(summary)
            
            # Save summary to file
            summary_path = os.path.join(self.output_dir, "etl_summary.txt")
            with open(summary_path, 'w') as f:
                f.write(summary)
                
            logger.info(f"ETL completed successfully. Summary saved to {summary_path}")
            
        except Exception as e:
            logger.error(f"ETL failed with error: {e}")
            raise


def main():
    """Main function to run the ETL process."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(project_root, "data")
    output_dir = os.path.join(project_root, "data", "star_schema")
    
    # Run ETL
    etl = VehicleMarketStarSchemaETL(data_dir=data_dir, output_dir=output_dir)
    etl.run_etl()


if __name__ == "__main__":
    main()
