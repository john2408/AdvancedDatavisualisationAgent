# Vehicle Registered Data Traditional Star Schema

## Overview

This traditional star schema is designed to provide **optimal data normalization** and **analytical performance** for vehicle registration data. This model follows classic dimensional modeling principles with a fully normalized fact table that contains only foreign keys and measures, requiring joins to access descriptive attributes.

## Traditional Star Schema Design

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
             │     ┌──────────────────────────────────────────────────┐     │
             └────▶│            FactRegisteredVehicles                │◀────┘
                   │                                                  │
                   │ PK: vehicle_count_id                             │
                   │ FK: time_key, oem_key, vehicle_key               │
                   │ FK: geography_country_key, geography_district_key│
                   │                                                  │
                   │ FOREIGN KEYS (NORMALIZED DESIGN):               │
                   │ • time_key → DimTime                            │
                   │ • oem_key → DimOEM                              │
                   │ • vehicle_key → DimVehicle                      │
                   │ • geography_country_key → DimGeographyCountry   │
                   │ • geography_district_key → DimGeographyDistrict │
                   │                                                  │
                   │ MEASURE:                                        │
                   │ • vehicle_count (numeric measure)               │
                   │                                                  │
                   │ Note: All descriptive attributes accessed       │
                   │ through dimension table joins                   │
                   └──────────────────────────────────────────────────┘
                                    │
                                    │
        ┌─────────────────────────────────┐    ┌─────────────────────────────────┐
        │    DimGeographyCountry          │    │      DimGeographyDistrict       │
        │                                 │    │                                 │
        │ PK: geography_country_key       │    │ PK: geography_district_key      │
        │    country_name                 │    │    country_name                 │
        │    country_code                 │    │    country_code                 │
        └─────────────────────────────────┘    │    region_name                  │
                                               │    district_postcode            │
                                               │    district_town_name           │
                                               │    full_location_path           │
                                               └─────────────────────────────────┘
```

## Key Advantages of Traditional Star Schema

### 📊 **Data Normalization**
1. **Minimal Redundancy**: Each attribute stored only once in appropriate dimension
2. **Data Consistency**: Single source of truth for all descriptive attributes
3. **Storage Efficiency**: Optimized storage through normalized design
4. **Referential Integrity**: Strong foreign key relationships ensure data quality

### ⚡ **Analytical Performance**
1. **Optimized Joins**: Efficient join operations with proper indexing
2. **Flexible Aggregation**: Sum measures at any dimensional level
3. **Scalable Design**: Handles large data volumes efficiently
4. **Query Optimization**: Database engines optimize join patterns well

### � **Maintenance Benefits**
1. **Easy Updates**: Dimension updates affect all related facts automatically
2. **Data Quality**: Centralized dimension management
3. **Schema Evolution**: Easy to add new dimensions or attributes
4. **Standard Design**: Follows established dimensional modeling principles

## Table Definitions

### Traditional Fact Table: FactRegisteredVehicles

| Column | Type | Purpose | Description |
|--------|------|---------|-------------|
| **PRIMARY KEY** | | | |
| vehicle_count_id | TEXT | PK | Unique identifier for each registration record |
| **FOREIGN KEYS** | | | |
| time_key | INTEGER | FK → DimTime | Links to time dimension for temporal analysis |
| oem_key | INTEGER | FK → DimOEM | Links to OEM dimension for manufacturer details |
| vehicle_key | INTEGER | FK → DimVehicle | Links to vehicle dimension for type details |
| geography_country_key | INTEGER | FK → DimGeographyCountry | Links to country dimension |
| geography_district_key | INTEGER | FK → DimGeographyDistrict | Links to district dimension |
| **MEASURE** | | | |
| vehicle_count | INTEGER | Measure | Number of vehicles registered (additive measure) |

**Note:** All descriptive attributes (manufacturer names, vehicle types, geographic details, etc.) are accessed through joins with dimension tables.

### Dimension Tables (Complete Original Star Schema)

All dimension tables provide the descriptive context for the fact table:
- **DimTime**: Time dimension with quarters, years, months, and temporal hierarchies
- **DimOEM**: Manufacturer details with categories, origins, and company information
- **DimVehicle**: Vehicle type characteristics including body type and fuel type combinations
- **DimGeographyCountry**: Country-level geography with codes and names
- **DimGeographyDistrict**: District-level detailed geography with full hierarchical paths

## Query Pattern Examples

### 📊 **Traditional Star Schema Queries** (Requires Joins)

```sql
-- "How many BMW vehicles were registered in 2024?"
SELECT SUM(f.vehicle_count) 
FROM FactRegisteredVehicles f
JOIN DimOEM o ON f.oem_key = o.oem_key
JOIN DimTime t ON f.time_key = t.time_key
WHERE o.oem_name = 'BMW' AND t.year_report = 2024;

-- "What are the top electric vehicle registrations by region?"
SELECT 
    gd.region_name, 
    SUM(f.vehicle_count) as total
FROM FactRegisteredVehicles f
JOIN DimVehicle v ON f.vehicle_key = v.vehicle_key
JOIN DimGeographyDistrict gd ON f.geography_district_key = gd.geography_district_key
WHERE v.fuel_type = 'ELECTRIC'
GROUP BY gd.region_name
ORDER BY total DESC;

-- "Show monthly Tesla registrations"
SELECT 
    t.year_report, 
    t.month_report, 
    SUM(f.vehicle_count) as total_registrations
FROM FactRegisteredVehicles f
JOIN DimOEM o ON f.oem_key = o.oem_key
JOIN DimTime t ON f.time_key = t.time_key
WHERE o.oem_name = 'Tesla'
GROUP BY t.year_report, t.month_report
ORDER BY t.year_report, t.month_report;
```

### � **Advanced Analytical Queries** (Complex Joins)

```sql
-- "Compare luxury vs mass market registrations by quarter"
SELECT 
    t.quarter,
    o.oem_category,
    SUM(f.vehicle_count) as total_registrations
FROM FactRegisteredVehicles f
JOIN DimTime t ON f.time_key = t.time_key
JOIN DimOEM o ON f.oem_key = o.oem_key
WHERE o.oem_category IN ('Luxury', 'Mass Market')
GROUP BY t.quarter, o.oem_category
ORDER BY t.quarter, o.oem_category;

-- "Regional analysis with full geographic hierarchy"
SELECT 
    gc.country_name,
    gd.region_name,
    gd.district_town_name,
    v.body_type,
    v.fuel_type,
    SUM(f.vehicle_count) as registrations
FROM FactRegisteredVehicles f
JOIN DimGeographyCountry gc ON f.geography_country_key = gc.geography_country_key
JOIN DimGeographyDistrict gd ON f.geography_district_key = gd.geography_district_key
JOIN DimVehicle v ON f.vehicle_key = v.vehicle_key
GROUP BY gc.country_name, gd.region_name, gd.district_town_name, v.body_type, v.fuel_type
ORDER BY registrations DESC;

-- "Time series analysis with moving averages"
SELECT 
    t.year_month,
    o.oem_name,
    SUM(f.vehicle_count) as monthly_registrations,
    AVG(SUM(f.vehicle_count)) OVER (
        PARTITION BY o.oem_name 
        ORDER BY t.year_month 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as three_month_avg
FROM FactRegisteredVehicles f
JOIN DimTime t ON f.time_key = t.time_key
JOIN DimOEM o ON f.oem_key = o.oem_key
GROUP BY t.year_month, o.oem_name
ORDER BY o.oem_name, t.year_month;
```

## Indexing Strategy

### **Foreign Key Indexes** (Join Optimization)
```sql
-- Primary indexes for fact table joins
CREATE INDEX idx_factvehicles_time ON FactRegisteredVehicles(time_key);
CREATE INDEX idx_factvehicles_oem ON FactRegisteredVehicles(oem_key);
CREATE INDEX idx_factvehicles_vehicle ON FactRegisteredVehicles(vehicle_key);
CREATE INDEX idx_factvehicles_country ON FactRegisteredVehicles(geography_country_key);
CREATE INDEX idx_factvehicles_district ON FactRegisteredVehicles(geography_district_key);
```

### **Dimension Table Indexes** (Lookup Optimization)
```sql
-- Dimension table lookup indexes
CREATE INDEX idx_dimtime_year_month ON DimTime(year_report, month_report);
CREATE INDEX idx_dimoem_name ON DimOEM(oem_name);
CREATE INDEX idx_dimvehicle_body_fuel ON DimVehicle(body_type, fuel_type);
CREATE INDEX idx_dimgeocountry_name ON DimGeographyCountry(country_name);
CREATE INDEX idx_dimgeodistrict_country_region ON DimGeographyDistrict(country_name, region_name);
```

### **Composite Indexes** (Complex Query Patterns)
```sql
-- Multi-column indexes for common join combinations
CREATE INDEX idx_factvehicles_time_oem ON FactRegisteredVehicles(time_key, oem_key);
CREATE INDEX idx_factvehicles_time_vehicle ON FactRegisteredVehicles(time_key, vehicle_key);
CREATE INDEX idx_factvehicles_oem_vehicle ON FactRegisteredVehicles(oem_key, vehicle_key);
```

## Traditional Star Schema Benefits

### 🎯 **Data Integrity and Consistency**
1. **Single Source of Truth**: Each dimension attribute exists only once
2. **Referential Integrity**: Strong foreign key constraints ensure data quality
3. **Normalized Structure**: Eliminates data redundancy and inconsistencies
4. **Centralized Updates**: Change dimension data once, affects all related facts

### 🚀 **Performance and Scalability**
1. **Optimized Storage**: Minimal data redundancy saves storage space
2. **Efficient Joins**: Database engines optimize star schema join patterns
3. **Indexed Access**: Foreign key indexes enable fast join operations
4. **Scalable Design**: Handles large volumes through proper normalization

### 🧠 **Analytical Flexibility**
1. **Rich Context**: Full dimensional attributes available through joins
2. **Hierarchical Analysis**: Navigate geographic and temporal hierarchies
3. **Cross-Dimensional**: Analyze relationships across multiple dimensions
4. **Aggregation Levels**: Sum measures at any dimensional granularity

### 🔧 **Enterprise Standards**
1. **Industry Standard**: Follows established dimensional modeling practices
2. **Tool Compatibility**: Works with all BI and analytical tools
3. **Maintainable Design**: Clear separation of facts and dimensions
4. **Documentation**: Well-understood by data professionals

## Traditional Star Schema Design

### **What This Implementation Provides**
- ✅ **Normalized Fact Table**: Only foreign keys and measures in FactRegisteredVehicles
- ✅ **Complete Dimension Tables**: All descriptive attributes in proper dimensions
- ✅ **Referential Integrity**: Strong FK constraints maintain data quality
- ✅ **Optimized Joins**: Efficient join performance with proper indexing
- ✅ **Standard Design**: Follows Ralph Kimball's dimensional modeling principles

### **Traditional Star Schema Characteristics**
- ✅ **Fact Table**: Contains only foreign keys, measures, and business keys
- ✅ **Dimension Tables**: Rich descriptive attributes and hierarchies
- ✅ **Join Requirements**: All queries requiring attributes must join dimensions
- ✅ **Storage Efficiency**: Minimal redundancy through normalization
- ✅ **Data Consistency**: Single source of truth for all dimensional attributes

## Best Practices for Traditional Star Schema

### **Query Development Guidelines**
1. **Start with Measures**: Identify required facts and measures first
2. **Add Dimensions**: Join only necessary dimensions for required attributes
3. **Use Indexes**: Leverage foreign key indexes for optimal join performance
4. **Filter Early**: Apply WHERE clauses before expensive joins when possible

### **Performance Optimization**
1. **Index Strategy**: Ensure proper indexing on all foreign keys
2. **Join Order**: Let the query optimizer determine optimal join sequences
3. **Dimension Size**: Keep dimension tables reasonably sized for join efficiency
4. **Query Patterns**: Design indexes based on common query access patterns

This traditional star schema provides the **proven benefits** of dimensional modeling: data consistency, storage efficiency, and analytical flexibility through a normalized design that follows industry best practices.
