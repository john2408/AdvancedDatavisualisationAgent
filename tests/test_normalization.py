#!/usr/bin/env python3
"""
Test script for normalized stacked bar chart functionality
"""

import pandas as pd
import json

def test_stacked_bar_normalization():
    """Test the normalization logic for stacked bar charts"""
    
    # Create test data similar to monthly registrations for multiple car brands
    test_data = [
        {"month": "Jan", "brand": "MERCEDES-BENZ", "registrations": 150},
        {"month": "Jan", "brand": "BMW", "registrations": 120},
        {"month": "Jan", "brand": "AUDI", "registrations": 100},
        {"month": "Feb", "brand": "MERCEDES-BENZ", "registrations": 180},
        {"month": "Feb", "brand": "BMW", "registrations": 140},
        {"month": "Feb", "brand": "AUDI", "registrations": 80},
        {"month": "Mar", "brand": "MERCEDES-BENZ", "registrations": 200},
        {"month": "Mar", "brand": "BMW", "registrations": 160},
        {"month": "Mar", "brand": "AUDI", "registrations": 90},
    ]
    
    df = pd.DataFrame(test_data)
    print("Original DataFrame:")
    print(df)
    print()
    
    # Simulate normalization logic
    x_column = "month"
    y_column = "registrations"
    color_column = "brand"
    
    # Calculate totals per month
    totals_per_month = df.groupby(x_column)[y_column].sum()
    print("Totals per month:")
    print(totals_per_month)
    print()
    
    # Create normalized version
    df_normalized = df.copy()
    df_normalized[f'{y_column}_normalized'] = 0.0
    
    for month in df_normalized[x_column].unique():
        mask = df_normalized[x_column] == month
        total_for_month = totals_per_month[month]
        if total_for_month > 0:
            df_normalized.loc[mask, f'{y_column}_normalized'] = (
                df_normalized.loc[mask, y_column] / total_for_month * 100
            ).round(2)
    
    # Replace original values with normalized values
    df_normalized[y_column] = df_normalized[f'{y_column}_normalized']
    df_normalized = df_normalized.drop(columns=[f'{y_column}_normalized'])
    
    print("Normalized DataFrame:")
    print(df_normalized)
    print()
    
    # Verify normalization (each month should sum to 100%)
    verification = df_normalized.groupby(x_column)[y_column].sum()
    print("Verification - Sum per month (should be ~100%):")
    print(verification)
    print()
    
    # Test JSON conversion
    df_json = df_normalized.to_json(orient='records')
    print("JSON representation:")
    print(df_json)
    
    print("✅ Stacked bar normalization test completed!")
    return df_normalized

if __name__ == "__main__":
    test_stacked_bar_normalization()
