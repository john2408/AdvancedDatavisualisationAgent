#!/usr/bin/env python3
"""
Unit Tests for Plot Generation Validation

This module contains tests to validate the chart type selection logic
in the visualization generation pipeline.
"""

import unittest
import pandas as pd
import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the function to test
from frontend.analytics_selector import return_chart_type, ChartType, create_chart_plan, ChartPlan


class TestPlotGeneration(unittest.TestCase):
    """Test cases for plot generation and chart type selection."""
    
    @staticmethod
    def load_test_dataframe_from_json(filename="monthly_registrations.json"):
        """Load test DataFrame from JSON file in test_data directory."""
        
        json_file_path = project_root / "tests" / "test_data" / filename
        
        if not json_file_path.exists():
            raise FileNotFoundError(f"Test data file not found: {json_file_path}")
        
        with open(json_file_path, 'r') as f:
            json_data = json.load(f)
        
        # Convert JSON to DataFrame (matching the pandas.to_json() format)
        test_dataframe = pd.DataFrame(json_data)
        
        # Ensure year_month is properly formatted as datetime
        if 'year_month' in test_dataframe.columns:
            test_dataframe['year_month'] = pd.to_datetime(test_dataframe['year_month'])
        
        return test_dataframe
 
 
    def test_chart_type_enum_values(self):
        """Test that ChartType enum contains expected values."""
        expected_chart_types = [
            'BAR', 'STACKED_BAR', 'LINE', 'MULTI_LINE', 
            'PIE', 'SCATTER', 'HISTOGRAM', 'BOX', 'HEATMAP'
        ]
        
        actual_chart_types = [chart_type.value for chart_type in ChartType]
        
        for expected_type in expected_chart_types:
            self.assertIn(
                expected_type, 
                actual_chart_types,
                f"ChartType enum should contain '{expected_type}'"
            )
        
        print(f"✅ ChartType enum validation passed")

        
    def test_monthly_registrations_returns_line_chart(self):
        """
        Test that return_chart_type returns LINE for monthly registrations query.
        
        This test validates that when given:
        - A DataFrame with time series data (year_month and total_registrations)
        - A user query asking for monthly registrations over time
        
        The function returns ChartType.MULTI_LINE as expected.
        """

        # Call the function to set up test data
        self.test_dataframe = self.load_test_dataframe_from_json(filename="monthly_registrations.json")    
    
        # Test input values
        user_query = "What are the monthly registrations in total since 2023?"
        
        # Validate test data structure
        self.assertIsInstance(self.test_dataframe, pd.DataFrame)
        self.assertFalse(self.test_dataframe.empty, "Test DataFrame should not be empty")
        self.assertIn('year_month', self.test_dataframe.columns, "DataFrame should contain 'year_month' column")
        
        # Print debug information
        print(f"\nTest DataFrame shape: {self.test_dataframe.shape}")
        print(f"Test DataFrame columns: {list(self.test_dataframe.columns)}")
        print(f"Test DataFrame data types:\n{self.test_dataframe.dtypes}")
        print(f"Sample data:\n{self.test_dataframe.head(3)}")
        
        # Call the function under test
        result_chart_type = return_chart_type(user_query, self.test_dataframe)
        
        # Validate the result
        self.assertEqual(
            result_chart_type, 
            ChartType.LINE.value,
            f"Expected {ChartType.LINE.value}, but got {result_chart_type}"
        )
        
        print(f"✅ Test passed: return_chart_type returned '{result_chart_type}' as expected")

    
    def test_monthly_electric_veh_returns_line_chart(self):
        """
        Test that return_chart_type returns LINE for monthly electric vehicle registrations query.
        """

        # Call the function to set up test data
        self.test_dataframe = self.load_test_dataframe_from_json(filename="monthly_electric_vehicles.json")

        # Test input values
        user_query = "What are the trends in monthly registrations of electric vehicles since 2023?"
        
        # Validate test data structure
        self.assertIsInstance(self.test_dataframe, pd.DataFrame)
        self.assertFalse(self.test_dataframe.empty, "Test DataFrame should not be empty")
        self.assertIn('year_month', self.test_dataframe.columns, "DataFrame should contain 'year_month' column")
        
        # Print debug information
        print(f"\nTest DataFrame shape: {self.test_dataframe.shape}")
        print(f"Test DataFrame columns: {list(self.test_dataframe.columns)}")
        print(f"Test DataFrame data types:\n{self.test_dataframe.dtypes}")
        print(f"Sample data:\n{self.test_dataframe.head(3)}")
        
        # Call the function under test
        result_chart_type = return_chart_type(user_query, self.test_dataframe)
        
        # Validate the result
        self.assertEqual(
            result_chart_type, 
            ChartType.LINE.value,
            f"Expected {ChartType.LINE.value}, but got {result_chart_type}"
        )
        
        print(f"✅ Test passed: return_chart_type returned '{result_chart_type}' as expected")


    def test_monthly_bmw_audi_return_multiline_chart(self):
        """
        Test that return_chart_type returns MULTI_LINE for monthly BMW and Audi registrations query.
        """

        # Call the function to set up test data
        self.test_dataframe = self.load_test_dataframe_from_json(filename="BMW_AUDI_monthly_registrations.json")

        # Test input values
        user_query = "What are the trends in monthly registrations of BMW and Audi vehicles since 2023?"

        # Validate test data structure
        self.assertIsInstance(self.test_dataframe, pd.DataFrame)
        self.assertFalse(self.test_dataframe.empty, "Test DataFrame should not be empty")
        self.assertIn('year_month', self.test_dataframe.columns, "DataFrame should contain 'year_month' column")
        
        # Print debug information
        print(f"\nTest DataFrame shape: {self.test_dataframe.shape}")
        print(f"Test DataFrame columns: {list(self.test_dataframe.columns)}")
        print(f"Test DataFrame data types:\n{self.test_dataframe.dtypes}")
        print(f"Sample data:\n{self.test_dataframe.head(3)}")
        
        # Call the function under test
        result_chart_type = return_chart_type(user_query, self.test_dataframe)
        
        # Validate the result
        self.assertEqual(
            result_chart_type, 
            ChartType.MULTI_LINE.value,
            f"Expected {ChartType.MULTI_LINE.value}, but got {result_chart_type}"
        )
        
        print(f"✅ Test passed: return_chart_type returned '{result_chart_type}' as expected")


    def test_create_chart_plan_bmw_audi_multiline(self):
        """
        Test that create_chart_plan returns correct ChartPlan object for BMW/AUDI multi-line query.
        
        This test validates that when given:
        - A DataFrame with time series data grouped by OEM (year_month, oem_name, monthly_registrations)
        - A user query asking for BMW, AUDI, MERCEDES-BENZ trends
        
        The function returns a ChartPlan object matching the expected structure.
        """
        
        # Load test data
        self.test_dataframe = self.load_test_dataframe_from_json(filename="BMW_AUDI_monthly_registrations.json")
        
        # Load expected ChartPlan structure
        expected_plan_path = project_root / "tests" / "test_data" / "chart_plan_BMW_AUDI.json"
        with open(expected_plan_path, 'r') as f:
            expected_plan_dict = json.load(f)
        
        # Test input values
        user_query = "What are the trends in monthly registrations of BMW, AUDI, MERCEDES-BENZ vehicles since 2023?"
        
        # Validate test data structure
        self.assertIsInstance(self.test_dataframe, pd.DataFrame)
        self.assertFalse(self.test_dataframe.empty, "Test DataFrame should not be empty")
        self.assertIn('year_month', self.test_dataframe.columns, "DataFrame should contain 'year_month' column")
        self.assertIn('oem_name', self.test_dataframe.columns, "DataFrame should contain 'oem_name' column")
        self.assertIn('monthly_registrations', self.test_dataframe.columns, "DataFrame should contain 'monthly_registrations' column")
        
        # Print debug information
        print(f"\nTest DataFrame shape: {self.test_dataframe.shape}")
        print(f"Test DataFrame columns: {list(self.test_dataframe.columns)}")
        print(f"Test DataFrame data types:\n{self.test_dataframe.dtypes}")
        print(f"Sample data:\n{self.test_dataframe.head(3)}")
        print(f"Expected ChartPlan: {expected_plan_dict}")
        
        # Call the function under test
        result_chart_plan = create_chart_plan(self.test_dataframe, user_query)
        
        # Validate the result is a ChartPlan object
        self.assertIsInstance(result_chart_plan, ChartPlan, "Result should be a ChartPlan instance")
        
        # Convert result to dictionary for comparison
        result_plan_dict = result_chart_plan.model_dump()
        
        # Validate each field of the ChartPlan
        self.assertEqual(
            result_plan_dict['chart_type'], 
            expected_plan_dict['chart_type'],
            f"Expected chart_type '{expected_plan_dict['chart_type']}', but got '{result_plan_dict['chart_type']}'"
        )
        
        self.assertEqual(
            result_plan_dict['x'], 
            expected_plan_dict['x'],
            f"Expected x column '{expected_plan_dict['x']}', but got '{result_plan_dict['x']}'"
        )
        
        self.assertEqual(
            result_plan_dict['y'], 
            expected_plan_dict['y'],
            f"Expected y columns {expected_plan_dict['y']}, but got {result_plan_dict['y']}"
        )
        
        self.assertEqual(
            result_plan_dict['color'], 
            expected_plan_dict['color'],
            f"Expected color column '{expected_plan_dict['color']}', but got '{result_plan_dict['color']}'"
        )
        
        self.assertEqual(
            result_plan_dict['aggregation'], 
            expected_plan_dict['aggregation'],
            f"Expected aggregation '{expected_plan_dict['aggregation']}', but got '{result_plan_dict['aggregation']}'"
        )
        
        self.assertEqual(
            result_plan_dict['transform'], 
            expected_plan_dict['transform'],
            f"Expected transform '{expected_plan_dict['transform']}', but got '{result_plan_dict['transform']}'"
        )
        
        self.assertEqual(
            result_plan_dict['title'], 
            expected_plan_dict['title'],
            f"Expected title '{expected_plan_dict['title']}', but got '{result_plan_dict['title']}'"
        )
        
        print(f"✅ Test passed: create_chart_plan returned correct ChartPlan object")
        print(f"   Chart Type: {result_plan_dict['chart_type']}")
        print(f"   X Column: {result_plan_dict['x']}")
        print(f"   Y Columns: {result_plan_dict['y']}")
        print(f"   Color Column: {result_plan_dict['color']}")
        print(f"   Title: {result_plan_dict['title']}")
        
        


if __name__ == '__main__':
    # Configure test runner for verbose output
    unittest.main(verbosity=2)
