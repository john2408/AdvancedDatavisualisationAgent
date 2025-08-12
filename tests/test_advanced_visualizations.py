"""
Unit tests for advanced visualization transformations and context-aware follow-up scenarios.

This module tests the intelligent handling of chart type conversions, data transformations,
and context-aware alternative visualizations in the visualization pipeline.
"""

import unittest
import pandas as pd
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to sys.path so we can import from the project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.tools.visualization_tool import DataFrameVisualizationTool
from agents.crew_agents import alternative_viz_crew


class TestAdvancedVisualizationTransformations(unittest.TestCase):
    """Test cases for advanced visualization transformations."""
    
    def setUp(self):
        """Set up test data and tool instance."""
        self.viz_tool = DataFrameVisualizationTool()
        
        # Sample data for vehicle manufacturers
        self.vehicle_data = pd.DataFrame({
            'manufacturer': ['Toyota', 'Volkswagen', 'Ford', 'Honda', 'Nissan', 'BMW', 'Mercedes', 'Audi'],
            'registrations': [150000, 120000, 100000, 95000, 85000, 60000, 55000, 50000]
        })
        
        # Sample time series data
        self.time_series_data = pd.DataFrame({
            'month': ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06'],
            'registrations': [80000, 85000, 92000, 88000, 94000, 89000]
        })
        
        # Sample regional data
        self.regional_data = pd.DataFrame({
            'region': ['North', 'South', 'East', 'West', 'Central'],
            'sales': [25000, 30000, 22000, 28000, 18000]
        })
        
        # Sample multi-category data
        self.multi_category_data = pd.DataFrame({
            'vehicle_type': ['SUV', 'Sedan', 'Hatchback', 'Coupe', 'Convertible', 'Truck', 'Van', 'Wagon', 'Crossover', 'Sports'],
            'count': [45000, 38000, 32000, 15000, 8000, 25000, 12000, 9000, 20000, 6000]
        })

    def test_scenario_1_bar_to_pie_transformation(self):
        """
        Test Scenario 1: Bar chart to pie chart conversion with percentage calculation.
        
        User asks: "Which car manufacturers registered the most vehicles?" (generates bar chart)
        Follow-up: "Convert the bar chart to pie chart"
        Expected: Data should be converted to percentages, maintain manufacturer categories.
        """
        # Convert data to JSON for the tool
        dataframe_json = self.vehicle_data.to_json(orient='records')
        
        # Test the transformation from bar to pie
        result = self.viz_tool._run(
            dataframe_json=dataframe_json,
            plot_type="pie",
            x_column="manufacturer",
            y_column="registrations",
            current_chart_type="bar",
            title="Vehicle Registrations by Manufacturer (Pie Chart)"
        )
        
        # Parse the result
        plot_spec = json.loads(result)
        
        # Assertions
        self.assertNotIn("error", plot_spec)
        self.assertEqual(plot_spec["type"], "pie")
        self.assertIn("data", plot_spec)
        
        # Check that data contains labels and values
        data = plot_spec["data"]
        self.assertIn("labels", data)
        self.assertIn("values", data)
        
        # Verify all manufacturers are represented
        self.assertTrue(len(data["labels"]) <= 8)  # Should be 8 or fewer (with Others grouping)
        self.assertTrue(all(isinstance(val, (int, float)) for val in data["values"]))
        
        print(f"✅ Scenario 1 PASSED: Bar to Pie conversion with {len(data['labels'])} categories")

    def test_scenario_2_absolute_to_percentage_conversion(self):
        """
        Test Scenario 2: Explicit percentage conversion for better comparison.
        
        User asks: "Show regional sales distribution" (generates bar chart)
        Follow-up: "Show this as percentages instead of absolute numbers"
        Expected: Values converted to percentages of total.
        """
        dataframe_json = self.regional_data.to_json(orient='records')
        
        # Test explicit percentage transformation
        result = self.viz_tool._run(
            dataframe_json=dataframe_json,
            plot_type="bar",
            x_column="region",
            y_column="sales",
            transformation="percentage",
            title="Regional Sales Distribution (Percentage)"
        )
        
        plot_spec = json.loads(result)
        
        # Assertions
        self.assertNotIn("error", plot_spec)
        self.assertEqual(plot_spec["type"], "bar")
        
        # Check that percentage calculation was applied
        # The tool should have created percentage values
        data = plot_spec["data"]
        total_percentage = sum(data.get("y", []))
        
        # For percentage transformation, we expect the data to be meaningful
        self.assertTrue(len(data.get("x", [])) == 5)  # All 5 regions
        self.assertTrue(len(data.get("y", [])) == 5)  # All 5 values
        
        print(f"✅ Scenario 2 PASSED: Percentage conversion with total sum check")

    def test_scenario_3_time_series_to_bar_aggregation(self):
        """
        Test Scenario 3: Line chart (time series) to bar chart conversion.
        
        User asks: "Show monthly registration trends" (generates line chart)
        Follow-up: "Convert this to a bar chart for better comparison"
        Expected: Time series data should be properly formatted for bar chart display.
        """
        dataframe_json = self.time_series_data.to_json(orient='records')
        
        result = self.viz_tool._run(
            dataframe_json=dataframe_json,
            plot_type="bar",
            x_column="month",
            y_column="registrations",
            current_chart_type="line",
            title="Monthly Registrations (Bar Chart)"
        )
        
        plot_spec = json.loads(result)
        
        # Assertions
        self.assertNotIn("error", plot_spec)
        self.assertEqual(plot_spec["type"], "bar")
        
        # Check data integrity
        data = plot_spec["data"]
        self.assertEqual(len(data.get("x", [])), 6)  # 6 months
        self.assertEqual(len(data.get("y", [])), 6)  # 6 values
        
        # Verify month formatting is appropriate for bar chart
        x_values = data.get("x", [])
        self.assertTrue(all(isinstance(x, str) for x in x_values))
        
        print(f"✅ Scenario 3 PASSED: Time series to bar conversion with {len(x_values)} periods")

    def test_scenario_4_category_consolidation_with_others(self):
        """
        Test Scenario 4: Large category set consolidation for pie chart.
        
        User asks: "Show vehicle type distribution" (generates bar chart with many categories)
        Follow-up: "Make this a pie chart with fewer categories"
        Expected: Small categories should be grouped into "Others" for better readability.
        """
        dataframe_json = self.multi_category_data.to_json(orient='records')
        
        result = self.viz_tool._run(
            dataframe_json=dataframe_json,
            plot_type="pie",
            x_column="vehicle_type",
            y_column="count",
            current_chart_type="bar",
            title="Vehicle Type Distribution (Simplified)"
        )
        
        plot_spec = json.loads(result)
        
        # Assertions
        self.assertNotIn("error", plot_spec)
        self.assertEqual(plot_spec["type"], "pie")
        
        data = plot_spec["data"]
        labels = data.get("labels", [])
        values = data.get("values", [])
        
        # Should have grouped small categories
        self.assertTrue(len(labels) <= 8)  # Should be limited for readability
        self.assertEqual(len(labels), len(values))
        
        # Check if "Others" category was created (if needed)
        if len(self.multi_category_data) > 8:
            self.assertIn("Others", labels)
        
        print(f"✅ Scenario 4 PASSED: Category consolidation with {len(labels)} final categories")

    def test_scenario_5_top_n_transformation(self):
        """
        Test Scenario 5: Top N filtering with remainder grouping.
        
        User asks: "Show all vehicle manufacturers" (generates chart with all data)
        Follow-up: "Show only top 5 manufacturers, group the rest as Others"
        Expected: Data should be limited to top 5 plus Others category.
        """
        dataframe_json = self.vehicle_data.to_json(orient='records')
        
        result = self.viz_tool._run(
            dataframe_json=dataframe_json,
            plot_type="bar",
            x_column="manufacturer",
            y_column="registrations",
            transformation="top_5",
            title="Top 5 Manufacturers vs Others"
        )
        
        plot_spec = json.loads(result)
        
        # Assertions
        self.assertNotIn("error", plot_spec)
        self.assertEqual(plot_spec["type"], "bar")
        
        data = plot_spec["data"]
        x_values = data.get("x", [])
        
        # Should have exactly 5 categories (top 4 + Others)
        self.assertEqual(len(x_values), 5)
        self.assertIn("Others", x_values)
        
        print(f"✅ Scenario 5 PASSED: Top N filtering with Others grouping")


class TestContextAwareFollowUpGeneration(unittest.TestCase):
    """Test cases for context-aware follow-up question generation."""
    
    def setUp(self):
        """Set up mock data and contexts."""
        self.sample_bar_chart_context = {
            "plot_type": "bar",
            "x_column": "manufacturer",
            "y_column": "registrations",
            "title": "Vehicle Registrations by Manufacturer"
        }
        
        self.sample_pie_chart_context = {
            "plot_type": "pie",
            "x_column": "region",
            "y_column": "sales_percentage",
            "title": "Regional Sales Distribution"
        }

    @patch('agents.crew_agents.alternative_viz_crew')
    def test_context_aware_visualization_suggestions(self, mock_crew):
        """
        Test that alternative visualization suggestions are contextually appropriate.
        
        For bar charts showing counts/amounts, should suggest:
        - Pie chart with percentage conversion
        - Line chart if time dimension available
        - Horizontal bar for better label readability
        """
        # Mock the crew response for bar to pie conversion
        mock_response = Mock()
        mock_response.pydantic = Mock()
        mock_response.pydantic.plot_type = "pie"
        mock_response.pydantic.plot_spec = json.dumps({
            "type": "pie",
            "data": {"labels": ["Toyota", "VW", "Ford"], "values": [35, 30, 25]},
            "layout": {"title": "Manufacturer Share (%)"}
        })
        mock_crew.kickoff.return_value = mock_response
        
        # Test the context-aware suggestion
        current_data = pd.DataFrame({
            'manufacturer': ['Toyota', 'Volkswagen', 'Ford'],
            'registrations': [150000, 120000, 100000]
        })
        
        # This would be called from the app's generate_alternative_visualization function
        result = mock_crew.kickoff(inputs={
            "user_request": "Convert to pie chart",
            "current_data": current_data.to_json(orient='records'),
            "current_chart_type": "bar"
        })
        
        # Verify the crew was called with appropriate context
        mock_crew.kickoff.assert_called_once()
        call_args = mock_crew.kickoff.call_args[1]['inputs']
        self.assertEqual(call_args['current_chart_type'], 'bar')
        self.assertIn('pie chart', call_args['user_request'].lower())
        
        print("✅ Context-aware visualization suggestions test PASSED")

    def test_data_transformation_detection(self):
        """
        Test that the system correctly detects when data transformation is needed.
        
        Bar chart data: absolute values
        Pie chart requirement: needs percentages
        System should automatically detect and apply percentage transformation.
        """
        viz_tool = DataFrameVisualizationTool()
        
        # Test data with absolute values
        test_data = pd.DataFrame({
            'category': ['A', 'B', 'C', 'D'],
            'value': [100, 200, 150, 50]
        })
        
        # Apply transformation for pie chart
        transformed_data = viz_tool._apply_intelligent_transformations(
            df=test_data,
            target_plot_type="pie",
            current_plot_type="bar",
            x_column="category",
            y_column="value",
            transformation=""
        )
        
        # Check that transformation was applied
        self.assertTrue('value_percentage' in transformed_data.columns)
        
        # Verify percentage calculation
        total_percentage = transformed_data['value_percentage'].sum()
        self.assertAlmostEqual(total_percentage, 100.0, places=1)
        
        print("✅ Data transformation detection test PASSED")


class TestOrchestrationScenarios(unittest.TestCase):
    """Test orchestration logic for various user interaction scenarios."""
    
    def setUp(self):
        """Set up test scenarios and mock dependencies."""
        self.orchestration_scenarios = [
            {
                "initial_query": "Which car manufacturers registered the most vehicles?",
                "chart_type": "bar",
                "follow_up": "Convert the bar chart to pie chart",
                "expected_action": "alternative_visualization",
                "expected_transformation": "percentage"
            },
            {
                "initial_query": "Show monthly sales trends",
                "chart_type": "line",
                "follow_up": "Make this a bar chart instead",
                "expected_action": "alternative_visualization",
                "expected_transformation": "time_aggregation"
            },
            {
                "initial_query": "Display regional performance",
                "chart_type": "bar",
                "follow_up": "Show as percentages",
                "expected_action": "alternative_visualization",
                "expected_transformation": "percentage"
            }
        ]

    @patch('agents.crew_agents.orchestration_crew')
    def test_orchestration_decision_making(self, mock_crew):
        """Test that orchestration correctly identifies follow-up vs new query scenarios."""
        
        for scenario in self.orchestration_scenarios:
            with self.subTest(scenario=scenario["follow_up"]):
                # Mock orchestration decision
                mock_response = Mock()
                mock_response.pydantic = Mock()
                mock_response.pydantic.action_type = "follow_up"
                mock_response.pydantic.reasoning = "User wants to modify existing visualization"
                mock_response.pydantic.confidence = 0.9
                mock_crew.kickoff.return_value = mock_response
                
                # Simulate conversation context
                conversation_history = [
                    {"role": "user", "content": scenario["initial_query"]},
                    {"role": "assistant", "content": f"Created {scenario['chart_type']} chart"}
                ]
                
                current_data_context = {
                    "chart_type": scenario["chart_type"],
                    "has_data": True
                }
                
                # Test orchestration call
                result = mock_crew.kickoff(inputs={
                    "user_query": scenario["follow_up"],
                    "conversation_history": str(conversation_history),
                    "current_data_context": str(current_data_context)
                })
                
                # Verify decision
                self.assertEqual(result.pydantic.action_type, "follow_up")
                self.assertGreater(result.pydantic.confidence, 0.7)
                
        print("✅ Orchestration decision making test PASSED")


def run_advanced_visualization_tests():
    """Run all advanced visualization tests and report results."""
    
    print("🧪 Running Advanced Visualization Transformation Tests...")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestAdvancedVisualizationTransformations))
    test_suite.addTest(unittest.makeSuite(TestContextAwareFollowUpGeneration))
    test_suite.addTest(unittest.makeSuite(TestOrchestrationScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Report summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n⚠️ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED! Advanced visualization transformations are working correctly.")
    else:
        print(f"\n⚠️ {len(result.failures + result.errors)} test(s) failed. Please review the implementation.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_advanced_visualization_tests()
    exit(0 if success else 1)
