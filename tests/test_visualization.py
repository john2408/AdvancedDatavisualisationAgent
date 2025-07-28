#!/usr/bin/env python3

"""
Simple test script for the new DataFrameVisualizationTool
"""

import pandas as pd
import json
from agents.tools.visualization_tool import DataFrameVisualizationTool

def test_visualization_tool():
    """Test the DataFrameVisualizationTool with sample data"""
    
    # Create sample data similar to our vehicle registration database
    sample_data = {
        'oem_name': ['BMW', 'AUDI', 'MERCEDES-BENZ', 'TESLA', 'FORD'],
        'vehicle_count': [15000, 12000, 18000, 8000, 25000],
        'month_report': [1, 1, 1, 1, 1],
        'body_type': ['SUV', 'SEDAN', 'SUV', 'SEDAN', 'SUV']
    }
    
    df = pd.DataFrame(sample_data)
    print("Sample DataFrame:")
    print(df)
    print()
    
    # Convert to JSON format as expected by the tool
    dataframe_json = df.to_json(orient='records')
    print("DataFrame JSON:")
    print(dataframe_json)
    print()
    
    # Initialize the tool
    viz_tool = DataFrameVisualizationTool()
    
    # Test different plot types
    test_cases = [
        {
            "plot_type": "bar",
            "x_column": "oem_name",
            "y_column": "vehicle_count",
            "title": "Vehicle Count by OEM"
        },
        {
            "plot_type": "pie",
            "x_column": "oem_name",
            "y_column": "vehicle_count",
            "title": "Market Share Distribution"
        },
        {
            "plot_type": "bar",
            "x_column": "oem_name",
            "y_column": "vehicle_count",
            "color_column": "body_type",
            "title": "Vehicle Count by OEM and Body Type"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"=== Test Case {i}: {test_case['plot_type'].upper()} CHART ===")
        
        result = viz_tool._run(
            dataframe_json=dataframe_json,
            plot_type=test_case["plot_type"],
            x_column=test_case["x_column"],
            y_column=test_case["y_column"],
            color_column=test_case.get("color_column", ""),
            title=test_case["title"]
        )
        
        try:
            result_json = json.loads(result)
            print(f"✅ Success! Generated {test_case['plot_type']} chart specification")
            print(f"Plot Type: {result_json.get('type', 'N/A')}")
            print(f"Title: {result_json.get('layout', {}).get('title', 'N/A')}")
            if 'error' in result_json:
                print(f"❌ Error: {result_json['error']}")
            print()
        except json.JSONDecodeError:
            print(f"❌ Failed to parse JSON result: {result}")
            print()

if __name__ == "__main__":
    test_visualization_tool()
