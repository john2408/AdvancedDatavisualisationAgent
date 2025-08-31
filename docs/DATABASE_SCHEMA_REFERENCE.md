# 📊 Database Schema Documentation
## UK Vehicle Registration Database - Complete Table Reference

This document provides a comprehensive overview of the database structure, including all tables, columns, data types, descriptions, and sample values to help AI agents understand how to filter and query the data correctly.

---

## 🗃️ Database Overview

**Database Type:** SQLite  
**Schema Design:** Traditional Star Schema  
**Data Coverage:** UK Vehicle Registration Data (2023-2024)  
**Total Records:** 625,476 fact records  
**Time Granularity:** Monthly data across 24 months  

---

## 📅 DimTime - Time Dimension Table

**Purpose:** Provides temporal context for all vehicle registration data  
**Row Count:** 24 records (12 months × 2 years)  
**Primary Key:** `time_key`

| Column | Data Type | Description | Sample Values | Notes |
|--------|-----------|-------------|---------------|-------|
| `time_key` | INTEGER | Primary key in YYYYMM format | `202301`, `202302`, `202412` | Use for joins with fact table |
| `year_report` | INTEGER | Year of registration | `2023`, `2024` | Filter: `WHERE year_report = 2024` |
| `month_report` | INTEGER | Month of registration (1-12) | `1`, `6`, `12` | Filter: `WHERE month_report IN (1,2,3)` for Q1 |
| `year_month` | TEXT | ISO date format for time series | `2023-01-01`, `2024-06-01` | **Use for time series plots** |
| `quarter` | INTEGER | Quarter number (1-4) | `1`, `2`, `3`, `4` | Filter: `WHERE quarter = 1` for Q1 |
| `year_quarter` | TEXT | Year and quarter combined | `2023-Q1`, `2024-Q4` | Filter: `WHERE year_quarter = '2024-Q1'` |

**Key Filtering Examples:**
```sql
-- Get Q1 data for both years
WHERE quarter = 1

-- Get 2024 data only  
WHERE year_report = 2024

-- Get specific months
WHERE month_report IN (1, 2, 3)

-- Get year-over-year comparison
WHERE year_quarter IN ('2023-Q1', '2024-Q1')

-- For time series plots (IMPORTANT)
ORDER BY year_month
```

---

## 🏭 DimOEM - Original Equipment Manufacturer Table

**Purpose:** Contains information about vehicle manufacturers  
**Row Count:** 14 records  
**Primary Key:** `oem_key`

| Column | Data Type | Description | Sample Values | Notes |
|--------|-----------|-------------|---------------|-------|
| `oem_key` | INTEGER | Primary key for OEM | `1`, `5`, `13`, `-1` | `-1` = Unknown OEM |
| `oem_name` | TEXT | Official manufacturer name | `BMW`, `TESLA`, `MERCEDES-BENZ` | **Exact case-sensitive matching required** |
| `oem_category` | TEXT | Business category classification | `Luxury`, `Premium`, `Mass Market` | Use for grouping analysis |
| `country_origin` | TEXT | Country where OEM is based | `Germany`, `UK`, `Japan`, `Sweden` | Geographic analysis of manufacturers |

**Available OEM Categories:**
- **Luxury:** `ASTON MARTIN`, `AUDI`, `BENTLEY`, `BMW`, `FERRARI`, `LAMBORGHINI`, `MASERATI`, `MERCEDES-BENZ`, `PORSCHE`
- **Premium:** `LEXUS`, `VOLVO`  
- **Mass Market:** `MINI`, `POLESTAR`
- **Unknown:** `Unknown`

**Key Filtering Examples:**
```sql
-- Filter by specific OEMs
WHERE oem_name IN ('BMW', 'AUDI', 'MERCEDES-BENZ')

-- Filter by category
WHERE oem_category = 'Luxury'

-- Filter by country of origin
WHERE country_origin = 'Germany'

-- Exclude unknown OEMs
WHERE oem_key != -1
```

---

## 🚗 DimVehicle - Vehicle Characteristics Table

**Purpose:** Defines vehicle types and specifications  
**Row Count:** 29 records  
**Primary Key:** `vehicle_key`

| Column | Data Type | Description | Sample Values | Notes |
|--------|-----------|-------------|---------------|-------|
| `vehicle_key` | INTEGER | Primary key for vehicle type | `1`, `15`, `28`, `-1` | `-1` = Unknown vehicle type |
| `body_type` | TEXT | Vehicle body style | `SUV`, `SEDAN`, `ESTATE`, `COUPE` | **Exact case-sensitive matching** |
| `fuel_type` | TEXT | Propulsion/fuel system | `PETROL`, `ELECTRIC`, `DIESEL` | **Use for EV analysis** |
| `vehicle_desc` | TEXT | Combined description | `SUV - PETROL`, `SEDAN - ELECTRIC` | Concatenated body_type - fuel_type |

**Available Body Types:**
- `SUV` (Most common)
- `SEDAN` 
- `ESTATE`
- `COUPE`
- `MPV`
- `SPORTSCOUPE`
- `CABRIO`
- `Unknown`

**Available Fuel Types:**
- `PETROL` (Gasoline vehicles)
- `ELECTRIC` (Battery electric vehicles - **Use for EV analysis**)
- `DIESEL` (Diesel vehicles)
- `PETROL/ELECTRIC` (Hybrid vehicles)
- `DIESEL/ELECTRIC` (Diesel hybrid vehicles)
- `Unknown`

**Key Filtering Examples:**
```sql
-- Electric vehicles only
WHERE fuel_type = 'ELECTRIC'

-- SUVs only
WHERE body_type = 'SUV'

-- All hybrid vehicles
WHERE fuel_type LIKE '%ELECTRIC' AND fuel_type != 'ELECTRIC'

-- Exclude unknown vehicles
WHERE vehicle_key != -1

-- Specific combinations
WHERE body_type = 'SUV' AND fuel_type = 'ELECTRIC'
```

---

## 🌍 DimGeographyCountry - Country-Level Geography

**Purpose:** Country-level geographic categorization  
**Row Count:** 9 records  
**Primary Key:** `geography_country_key`

| Column | Data Type | Description | Sample Values | Notes |
|--------|-----------|-------------|---------------|-------|
| `geography_country_key` | INTEGER | Primary key for country | `1`, `6`, `8`, `-1` | `-1` = Unknown country |
| `country_name` | TEXT | Official country name | `England`, `Scotland`, `Wales` | **UK constituent countries** |
| `country_code` | TEXT | Country code identifier | `GBR`, `UNK` | Mostly GBR for UK data |

**Available Countries (by registration volume):**
1. `England` (2,092 districts) - **Largest**
2. `Scotland` (403 districts)
3. `Wales` (183 districts)  
4. `Northern Ireland` (79 districts)
5. `Isle of Man` (9 districts)
6. `Guernsey` (8 districts)
7. `Jersey` (2 districts)
8. `N/A` (1 district)
9. `Unknown` (1 district)

**Key Filtering Examples:**
```sql
-- Main UK countries only
WHERE country_name IN ('England', 'Scotland', 'Wales', 'Northern Ireland')

-- England only (largest dataset)
WHERE country_name = 'England'

-- Exclude unknown locations
WHERE geography_country_key != -1
```

---

## 📍 DimGeographyDistrict - District-Level Geography

**Purpose:** Detailed geographic information down to district/town level  
**Row Count:** 2,778 records  
**Primary Key:** `geography_district_key`

| Column | Data Type | Description | Sample Values | Notes |
|--------|-----------|-------------|---------------|-------|
| `geography_district_key` | INTEGER | Primary key for district | `1`, `500`, `2777`, `-1` | `-1` = Unknown district |
| `country_name` | TEXT | Country name (denormalized) | `England`, `Scotland`, `Wales` | **Same as country table** |
| `country_code` | TEXT | Country code (denormalized) | `GBR`, `UNK` | Matches country table |
| `region_name` | TEXT | Administrative region/area | `Greater London`, `Birmingham`, `Edinburgh` | **Can be NULL** |
| `district_postcode` | TEXT | UK postal code area | `M28`, `BT45`, `EH1` | **Can be NULL** |
| `district_town_name` | TEXT | Town/city name | `Manchester`, `Belfast`, `Edinburgh` | **Can be NULL** |
| `full_location_path` | TEXT | Complete location hierarchy | `England / Greater London / London / (SW1A)` | **Always populated** |

**Sample Location Hierarchies:**
- `England / Greater London / London / (SW1A)`
- `Scotland / Edinburgh / Edinburgh / (EH1)`
- `Wales / Cardiff / Cardiff / (CF10)`
- `Northern Ireland / Belfast / Belfast / (BT1)`

**Key Filtering Examples:**
```sql
-- London area only
WHERE region_name = 'Greater London'

-- Major cities
WHERE district_town_name IN ('London', 'Birmingham', 'Manchester', 'Edinburgh')

-- By postcode area
WHERE district_postcode LIKE 'M%'  -- Manchester area

-- Exclude unknown districts
WHERE geography_district_key != -1

-- Specific location path
WHERE full_location_path LIKE 'England / Greater London%'
```

---

## 📊 FactRegisteredVehicles - Core Fact Table

**Purpose:** Contains actual vehicle registration counts (measures)  
**Row Count:** 625,476 records  
**Primary Key:** `vehicle_count_id`

| Column | Data Type | Description | Sample Values | Notes |
|--------|-----------|-------------|---------------|-------|
| `vehicle_count_id` | TEXT | Unique identifier for each record | `BMW_2024_01_England_London_SW1A_SUV_PETROL` | **Composite business key** |
| `time_key` | INTEGER | **Foreign key** to DimTime | `202301`, `202406`, `202412` | **Required for all time-based analysis** |
| `oem_key` | INTEGER | **Foreign key** to DimOEM | `3`, `7`, `12`, `-1` | **Required for OEM analysis** |
| `vehicle_key` | INTEGER | **Foreign key** to DimVehicle | `5`, `18`, `25`, `-1` | **Required for vehicle type analysis** |
| `geography_country_key` | INTEGER | **Foreign key** to DimGeographyCountry | `1`, `6`, `8`, `-1` | **Can be NULL** |
| `geography_district_key` | INTEGER | **Foreign key** to DimGeographyDistrict | `100`, `500`, `2000`, `-1` | **Can be NULL** |
| `vehicle_count` | INTEGER | **MEASURE**: Number of vehicles registered | `1`, `5`, `688` | **This is what you analyze/aggregate** |

**Data Characteristics:**
- **Total Records:** 625,476
- **Vehicle Count Range:** 1 to 688 vehicles per record
- **Average Count:** ~1.65 vehicles per record
- **Time Range:** January 2023 to December 2024 (24 months)
- **Null Foreign Keys:** Represented as `-1` (Unknown dimension entries)

**Critical Join Patterns:**
```sql
-- Basic fact table query structure
SELECT 
    d.dimension_attributes,
    SUM(f.vehicle_count) as total_registrations
FROM FactRegisteredVehicles f
JOIN DimTable d ON f.foreign_key = d.primary_key
WHERE filter_conditions
GROUP BY d.dimension_attributes
ORDER BY total_registrations DESC;

-- Time series analysis
SELECT 
    t.year_month,
    o.oem_name,
    SUM(f.vehicle_count) as monthly_registrations
FROM FactRegisteredVehicles f
JOIN DimTime t ON f.time_key = t.time_key
JOIN DimOEM o ON f.oem_key = o.oem_key
WHERE t.year_report = 2024
GROUP BY t.year_month, o.oem_name
ORDER BY t.year_month;
```

---

## 🔗 Foreign Key Relationships

**All joins must use these exact foreign key relationships:**

```sql
-- Time dimension
FactRegisteredVehicles.time_key = DimTime.time_key

-- OEM dimension  
FactRegisteredVehicles.oem_key = DimOEM.oem_key

-- Vehicle dimension
FactRegisteredVehicles.vehicle_key = DimVehicle.vehicle_key

-- Country geography
FactRegisteredVehicles.geography_country_key = DimGeographyCountry.geography_country_key

-- District geography
FactRegisteredVehicles.geography_district_key = DimGeographyDistrict.geography_district_key
```

---

## 🎯 Query Guidelines for AI Agents

### **1. Always Use Joins**
The fact table contains ONLY foreign keys and measures. All descriptive data requires joins:
```sql
-- ❌ WRONG - No descriptive context
SELECT SUM(vehicle_count) FROM FactRegisteredVehicles WHERE oem_key = 3;

-- ✅ CORRECT - With descriptive context
SELECT o.oem_name, SUM(f.vehicle_count) as total
FROM FactRegisteredVehicles f
JOIN DimOEM o ON f.oem_key = o.oem_key
WHERE o.oem_name = 'BMW';
```

### **2. Handle Unknown Values**
Unknown/missing data is represented with `-1` foreign keys:
```sql
-- Include unknowns
WHERE oem_key IS NOT NULL

-- Exclude unknowns  
WHERE oem_key != -1
```

### **3. Time Series Filtering**
Use appropriate time columns based on analysis type:
```sql
-- For time series plots - use year_month
ORDER BY t.year_month

-- For year-over-year comparison
WHERE t.year_report IN (2023, 2024)

-- For quarterly analysis
WHERE t.quarter = 1

-- For specific time periods
WHERE t.time_key BETWEEN 202301 AND 202312  -- All 2023
```

### **4. Case-Sensitive Filtering**
All text values are case-sensitive:
```sql
-- ✅ CORRECT
WHERE oem_name = 'BMW'
WHERE fuel_type = 'ELECTRIC'
WHERE country_name = 'England'

-- ❌ WRONG
WHERE oem_name = 'bmw'
WHERE fuel_type = 'electric'
```

### **5. Performance Optimization**
- Always join dimensions for descriptive data
- Use specific time ranges to limit data volume
- Index on foreign keys exists for optimal join performance
- Country-level queries are faster than district-level

---

## 📊 Common Analysis Patterns

### **Top OEMs by Registration Volume**
```sql
SELECT 
    o.oem_name,
    o.oem_category,
    SUM(f.vehicle_count) as total_registrations
FROM FactRegisteredVehicles f
JOIN DimOEM o ON f.oem_key = o.oem_key
WHERE o.oem_key != -1  -- Exclude unknown
GROUP BY o.oem_name, o.oem_category
ORDER BY total_registrations DESC;
```

### **Electric Vehicle Trend Analysis**
```sql
SELECT 
    t.year_month,
    SUM(f.vehicle_count) as ev_registrations
FROM FactRegisteredVehicles f
JOIN DimTime t ON f.time_key = t.time_key
JOIN DimVehicle v ON f.vehicle_key = v.vehicle_key
WHERE v.fuel_type = 'ELECTRIC'
GROUP BY t.year_month
ORDER BY t.year_month;
```

### **Market Share by Country**
```sql
WITH country_totals AS (
    SELECT 
        geography_country_key,
        SUM(vehicle_count) as total_vehicles
    FROM FactRegisteredVehicles 
    GROUP BY geography_country_key
)
SELECT 
    gc.country_name,
    o.oem_name,
    SUM(f.vehicle_count) as oem_vehicles,
    ct.total_vehicles,
    ROUND(SUM(f.vehicle_count) * 100.0 / ct.total_vehicles, 2) as market_share_pct
FROM FactRegisteredVehicles f
JOIN DimOEM o ON f.oem_key = o.oem_key
JOIN DimGeographyCountry gc ON f.geography_country_key = gc.geography_country_key
JOIN country_totals ct ON f.geography_country_key = ct.geography_country_key
WHERE f.geography_country_key != -1
GROUP BY gc.country_name, o.oem_name, ct.total_vehicles
ORDER BY gc.country_name, market_share_pct DESC;
```

---

This comprehensive schema documentation should help AI agents understand exactly how to structure queries, filter data correctly, and join tables appropriately for accurate analysis of the UK vehicle registration database.
