# Vehicle Market Share Star Schema Data Model

## Overview

This star schema is designed to support analytical queries for vehicle market share data across different geographic levels (country and district). The model normalizes the original fact tables into a dimensional structure optimized for business intelligence and reporting.

## Star Schema Design

```
                    ┌─────────────────┐
                    │   DimTime       │
                    │                 │
                    │ PK: time_key    │
                    │    year_report  │
                    │    month_report │
                    │    year_month   │
                    │    quarter      │
                    │    year_quarter │
                    └─────────────────┘
                             │
                             │
    ┌─────────────────┐     │     ┌─────────────────┐
    │    DimOEM       │     │     │  DimVehicle     │
    │                 │     │     │                 │
    │ PK: oem_key     │     │     │ PK: vehicle_key │
    │    oem_name     │     │     │    body_type    │
    │    oem_category │     │     │    fuel_type    │
    │    country_origin│    │     │    vehicle_desc │
    └─────────────────┘     │     └─────────────────┘
             │               │               │
             │               │               │
             │     ┌─────────────────────────────────┐     │
             └────▶│    FactMarketShareCountry       │◀────┘
                   │                                 │
                   │ PK: fact_country_key            │
                   │ FK: time_key                    │
                   │ FK: oem_key                     │
                   │ FK: vehicle_key                 │
                   │ FK: geography_country_key       │
                   │                                 │
                   │     total_vehicles_country      │
                   │     total_vehicles_country_oem  │
                   │     market_share_country        │
                   └─────────────────────────────────┘
                                    │
                                    │
                    ┌─────────────────────────────────┐
                    │      DimGeographyCountry        │
                    │                                 │
                    │ PK: geography_country_key       │
                    │    country_name                 │
                    │    country_code                 │
                    └─────────────────────────────────┘

             ┌─────────────────┐
             │    DimOEM       │
             │                 │
             │ PK: oem_key     │
             │    oem_name     │
             │    oem_category │
             │    country_origin│
             └─────────────────┘
                      │
                      │
             │     ┌─────────────────────────────────┐     │
             └────▶│    FactMarketShareDistrict      │◀────┘
                   │                                 │
                   │ PK: fact_district_key           │
                   │ FK: time_key                    │
                   │ FK: oem_key                     │
                   │ FK: vehicle_key                 │
                   │ FK: geography_district_key      │
                   │                                 │
                   │     total_vehicles_district     │
                   │     total_vehicles_district_oem │
                   │     market_share_district       │
                   └─────────────────────────────────┘
                                    │
                                    │
                    ┌─────────────────────────────────┐
                    │      DimGeographyDistrict       │
                    │                                 │
                    │ PK: geography_district_key      │
                    │    country_name                 │
                    │    country_code                 │
                    │    region_name                  │
                    │    district_postcode            │
                    │    district_town_name           │
                    │    full_location_path           │
                    └─────────────────────────────────┘
```

## Table Definitions

### Dimension Tables

#### DimTime
Time dimension for temporal analysis.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| time_key | INTEGER | Primary key (YYYYMM format) | PK, NOT NULL |
| year_report | INTEGER | Year of the report | NOT NULL |
| month_report | INTEGER | Month of the report (1-12) | NOT NULL |
| year_month | DATE | First day of the month | NOT NULL |
| quarter | INTEGER | Quarter (1-4) | NOT NULL |
| year_quarter | VARCHAR(7) | Year-Quarter (YYYY-Q1) | NOT NULL |

#### DimOEM
Original Equipment Manufacturer dimension.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| oem_key | INTEGER | Primary key (auto-increment) | PK, NOT NULL |
| oem_name | VARCHAR(100) | OEM name | NOT NULL, UNIQUE |
| oem_category | VARCHAR(50) | OEM category (Luxury, Premium, Mass Market) | Generated based on OEM |
| country_origin | VARCHAR(50) | Country of origin | Generated based on OEM |

#### DimVehicle
Vehicle characteristics dimension.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| vehicle_key | INTEGER | Primary key (auto-increment) | PK, NOT NULL |
| body_type | VARCHAR(50) | Body type of vehicle | NOT NULL |
| fuel_type | VARCHAR(50) | Fuel type of vehicle | NOT NULL |
| vehicle_desc | VARCHAR(150) | Concatenated description | Generated: body_type + fuel_type |

#### DimGeographyCountry
Country-level geography dimension.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| geography_country_key | INTEGER | Primary key (auto-increment) | PK, NOT NULL |
| country_name | VARCHAR(100) | Country name | NOT NULL, UNIQUE |
| country_code | VARCHAR(3) | ISO country code | Generated from country name |

#### DimGeographyDistrict
District-level geography dimension.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| geography_district_key | INTEGER | Primary key (auto-increment) | PK, NOT NULL |
| country_name | VARCHAR(100) | Country name | NOT NULL |
| country_code | VARCHAR(3) | ISO country code | Generated |
| region_name | VARCHAR(100) | Region name | NULL allowed |
| district_postcode | VARCHAR(20) | District postcode | NULL allowed |
| district_town_name | VARCHAR(100) | District town name | NULL allowed |
| full_location_path | VARCHAR(500) | Full path: Country/Region/District | Generated |

### Fact Tables

#### FactMarketShareCountry
Country-level market share fact table.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| fact_country_key | INTEGER | Primary key (auto-increment) | PK, NOT NULL |
| time_key | INTEGER | Foreign key to DimTime | FK, NOT NULL |
| oem_key | INTEGER | Foreign key to DimOEM | FK, NOT NULL |
| vehicle_key | INTEGER | Foreign key to DimVehicle | FK, NOT NULL |
| geography_country_key | INTEGER | Foreign key to DimGeographyCountry | FK, NOT NULL |
| total_vehicles_country | INTEGER | Total vehicles in country | NOT NULL |
| total_vehicles_country_oem | INTEGER | Total vehicles for OEM in country | NOT NULL |
| market_share_country | DECIMAL(8,6) | Market share percentage (0-1) | NOT NULL |

#### FactMarketShareDistrict
District-level market share fact table.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| fact_district_key | INTEGER | Primary key (auto-increment) | PK, NOT NULL |
| time_key | INTEGER | Foreign key to DimTime | FK, NOT NULL |
| oem_key | INTEGER | Foreign key to DimOEM | FK, NOT NULL |
| vehicle_key | INTEGER | Foreign key to DimVehicle | FK, NOT NULL |
| geography_district_key | INTEGER | Foreign key to DimGeographyDistrict | FK, NOT NULL |
| total_vehicles_district | INTEGER | Total vehicles in district | NOT NULL |
| total_vehicles_district_oem | INTEGER | Total vehicles for OEM in district | NOT NULL |
| market_share_district | DECIMAL(8,6) | Market share percentage (0-1) | NOT NULL |

## Data Generation Rules

### OEM Category Assignment
- **Luxury**: Mercedes-Benz, BMW, Audi, Porsche, Jaguar, Land Rover, Bentley, Rolls-Royce
- **Premium**: Volvo, Lexus, Infiniti, Acura, Genesis, Cadillac
- **Mass Market**: All others (Toyota, Ford, Volkswagen, etc.)

### Country of Origin Mapping
- **Germany**: BMW, Mercedes-Benz, Audi, Volkswagen, Porsche, Opel
- **Japan**: Toyota, Honda, Nissan, Mazda, Subaru, Mitsubishi, Lexus, Infiniti, Acura
- **USA**: Ford, Chevrolet, Cadillac, Buick, GMC, Chrysler, Dodge, Jeep, Lincoln
- **UK**: Jaguar, Land Rover, Bentley, Rolls-Royce, Mini, Aston Martin
- **France**: Peugeot, Citroën, Renault
- **Italy**: Fiat, Alfa Romeo, Ferrari, Lamborghini, Maserati
- **South Korea**: Hyundai, Kia, Genesis
- **Sweden**: Volvo, Saab

### Country Code Generation
- England → GBR
- Scotland → GBR  
- Wales → GBR
- Northern Ireland → GBR
- Germany → DEU
- France → FRA
- (Standard ISO 3166-1 alpha-3 codes)

## Indexing Strategy

### Primary Keys
- All dimension tables: Clustered index on primary key
- All fact tables: Clustered index on primary key

### Foreign Keys
- All foreign key columns in fact tables
- Composite indexes on frequently queried combinations

### Performance Indexes
- DimTime: (year_report, month_report)
- DimOEM: (oem_name)
- DimVehicle: (body_type, fuel_type)
- DimGeographyCountry: (country_name)
- DimGeographyDistrict: (country_name, region_name)
- FactMarketShareCountry: (time_key, oem_key), (time_key, vehicle_key)
- FactMarketShareDistrict: (time_key, oem_key), (time_key, vehicle_key)

## Sample Queries

### Top 5 OEMs by Market Share in England
```sql
SELECT 
    o.oem_name,
    AVG(f.market_share_country) as avg_market_share,
    SUM(f.total_vehicles_country_oem) as total_vehicles
FROM FactMarketShareCountry f
JOIN DimOEM o ON f.oem_key = o.oem_key
JOIN DimGeographyCountry g ON f.geography_country_key = g.geography_country_key
WHERE g.country_name = 'England'
GROUP BY o.oem_name
ORDER BY avg_market_share DESC
LIMIT 5;
```

### Monthly Market Share Trends for BMW Sedans
```sql
SELECT 
    t.year_month,
    AVG(f.market_share_country) as market_share
FROM FactMarketShareCountry f
JOIN DimTime t ON f.time_key = t.time_key
JOIN DimOEM o ON f.oem_key = o.oem_key
JOIN DimVehicle v ON f.vehicle_key = v.vehicle_key
WHERE o.oem_name = 'BMW' 
    AND v.body_type = 'SEDAN'
GROUP BY t.year_month
ORDER BY t.year_month;
```

### District-Level Analysis for Electric Vehicles
```sql
SELECT 
    g.country_name,
    g.region_name,
    g.district_town_name,
    SUM(f.total_vehicles_district_oem) as total_ev_vehicles,
    AVG(f.market_share_district) as avg_market_share
FROM FactMarketShareDistrict f
JOIN DimGeographyDistrict g ON f.geography_district_key = g.geography_district_key
JOIN DimVehicle v ON f.vehicle_key = v.vehicle_key
WHERE v.fuel_type = 'ELECTRIC'
GROUP BY g.country_name, g.region_name, g.district_town_name
ORDER BY total_ev_vehicles DESC;
```

## Data Quality Considerations

1. **Referential Integrity**: All foreign keys must reference valid dimension records
2. **Market Share Validation**: Market share values should be between 0 and 1
3. **Time Consistency**: All time_key values must exist in DimTime
4. **Geographic Hierarchy**: District records must have valid country references
5. **Duplicate Prevention**: Unique constraints on natural keys in dimensions
6. **NULL Handling**: Define clear rules for handling missing geographic data

## Benefits of This Design

1. **Query Performance**: Optimized for analytical queries with proper indexing
2. **Data Consistency**: Normalized dimensions reduce redundancy and ensure consistency
3. **Scalability**: Easy to add new time periods, OEMs, or vehicle types
4. **Flexibility**: Supports both country and district-level analysis
5. **Maintainability**: Clear separation of concerns between dimensions and facts
6. **Business Intelligence**: Ready for integration with BI tools and reporting frameworks
