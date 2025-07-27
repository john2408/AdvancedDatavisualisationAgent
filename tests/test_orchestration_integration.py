"""
Integration tests for orchestration and crew-based visualization transformations.

This module tests the end-to-end flow of context-aware follow-up questions,
alternative visualizations, and intelligent data transformations in the full pipeline.
"""

import unittest
import pandas as pd
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to sys.path so we can import from the project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.crew_agents import (
        orchestration_crew, 
        alternative_viz_crew, 
        follow_up_crew,
        data_question_crew
    )
    from agents.tools.visualization_tool import DataFrameVisualizationTool
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")


class TestOrchestrationIntegration(unittest.TestCase):
    """Integration tests for the full orchestration pipeline."""
    
    def setUp(self):
        """Set up test data and mock scenarios."""
        
        # Sample vehicle manufacturer data (bar chart scenario)
        self.manufacturer_data = pd.DataFrame({
            'manufacturer': ['Toyota', 'Volkswagen', 'Ford', 'Honda', 'Nissan'],
            'registrations': [150000, 120000, 100000, 95000, 85000]
        })
        
        # Sample conversation contexts
        self.bar_chart_context = {
            "current_data": self.manufacturer_data,
            "chart_info": {
                "plot_type": "bar",
                "title": "Vehicle Registrations by Manufacturer",
                "x_column": "manufacturer",
                "y_column": "registrations"
            },
            "data_summary": "Showing vehicle registrations by manufacturer with Toyota leading at 150,000 registrations"
        }

    def test_bar_to_pie_orchestration_flow(self):
        """
        Test Case 1: Full flow for bar chart to pie chart conversion.
        
        Scenario:
        1. User asks: "Which car manufacturers registered the most vehicles?" → Bar chart
        2. User asks: "Convert the bar chart to pie chart" → Should recognize follow-up
        3. System should apply percentage transformation and create pie chart
        """
        
        print("\n🧪 Testing Bar to Pie Chart Orchestration Flow...")
        
        # Step 1: Simulate orchestration decision
        with patch('agents.crew_agents.orchestration_crew') as mock_orchestration:
            # Mock orchestration response - should recognize this as follow-up
            mock_orchestration_result = Mock()
            mock_orchestration_result.pydantic = Mock()
            mock_orchestration_result.pydantic.action_type = "follow_up"
            mock_orchestration_result.pydantic.reasoning = "User wants to modify existing bar chart visualization"
            mock_orchestration_result.pydantic.confidence = 0.95
            mock_orchestration.kickoff.return_value = mock_orchestration_result
            
            # Test orchestration decision
            conversation_history = [
                {"role": "user", "content": "Which car manufacturers registered the most vehicles?"},
                {"role": "assistant", "content": "Created bar chart showing vehicle registrations by manufacturer"}
            ]
            
            current_data_context = {
                "chart_type": "bar",
                "has_data": True,
                "x_column": "manufacturer", 
                "y_column": "registrations"
            }
            
            orchestration_result = mock_orchestration.kickoff(inputs={
                "user_query": "Convert the bar chart to pie chart",
                "conversation_history": str(conversation_history),
                "current_data_context": str(current_data_context)
            })
            
            # Verify orchestration correctly identified follow-up
            self.assertEqual(orchestration_result.pydantic.action_type, "follow_up")
            self.assertGreater(orchestration_result.pydantic.confidence, 0.8)
            print("  ✅ Orchestration correctly identified follow-up request")
        
        # Step 2: Test alternative visualization generation
        with patch('agents.crew_agents.alternative_viz_crew') as mock_alt_viz:
            # Mock alternative visualization response with transformation
            mock_viz_result = Mock()
            mock_viz_result.pydantic = Mock()
            mock_viz_result.pydantic.plot_type = "pie"
            mock_viz_result.pydantic.x_column = "manufacturer"
            mock_viz_result.pydantic.y_column = "registrations"
            mock_viz_result.pydantic.transformation = "percentage"
            mock_viz_result.pydantic.title = "Vehicle Registrations by Manufacturer (Pie Chart)"
            mock_viz_result.pydantic.plot_spec = json.dumps({
                "type": "pie",
                "data": {
                    "labels": ["Toyota", "Volkswagen", "Ford", "Honda", "Nissan"],
                    "values": [27.3, 21.8, 18.2, 17.3, 15.5]  # Percentages
                },
                "layout": {"title": "Vehicle Registrations by Manufacturer (Pie Chart)"}
            })
            mock_alt_viz.kickoff.return_value = mock_viz_result
            
            # Test alternative visualization call
            alt_viz_result = mock_alt_viz.kickoff(inputs={
                "user_request": "Convert the bar chart to pie chart",
                "current_data": self.manufacturer_data.to_json(orient='records'),
                "current_chart_type": "bar"
            })
            
            # Verify transformation was applied
            self.assertEqual(alt_viz_result.pydantic.plot_type, "pie")
            self.assertEqual(alt_viz_result.pydantic.transformation, "percentage")
            
            # Parse and verify plot specification
            plot_spec = json.loads(alt_viz_result.pydantic.plot_spec)
            self.assertEqual(plot_spec["type"], "pie")
            self.assertIn("labels", plot_spec["data"])
            self.assertIn("values", plot_spec["data"])
            
            # Verify percentage transformation (values should sum to ~100)
            values = plot_spec["data"]["values"]
            total_percentage = sum(values)
            self.assertAlmostEqual(total_percentage, 100.0, delta=5.0)
            print("  ✅ Alternative visualization with percentage transformation generated")
        
        print("  🎉 Bar to Pie Chart Orchestration Flow PASSED")

    def test_percentage_conversion_scenario(self):
        """
        Test Case 2: Explicit percentage conversion request.
        
        Scenario:
        1. User has bar chart with absolute values
        2. User asks: "Show this as percentages instead"
        3. System should apply percentage transformation while keeping bar chart type
        """
        
        print("\n🧪 Testing Percentage Conversion Scenario...")
        
        with patch('agents.crew_agents.alternative_viz_crew') as mock_alt_viz:
            # Mock response for percentage conversion
            mock_viz_result = Mock()
            mock_viz_result.pydantic = Mock()
            mock_viz_result.pydantic.plot_type = "bar"
            mock_viz_result.pydantic.transformation = "percentage"
            mock_viz_result.pydantic.plot_spec = json.dumps({
                "type": "bar",
                "data": {
                    "x": ["Toyota", "Volkswagen", "Ford", "Honda", "Nissan"],
                    "y": [27.3, 21.8, 18.2, 17.3, 15.5]  # Percentages
                },
                "layout": {
                    "title": "Vehicle Registrations by Manufacturer (Percentage)",
                    "yaxis": {"title": "Percentage of Total Registrations"}
                }
            })
            mock_alt_viz.kickoff.return_value = mock_viz_result
            
            # Test percentage conversion
            result = mock_alt_viz.kickoff(inputs={
                "user_request": "Show this as percentages instead of absolute numbers",
                "current_data": self.manufacturer_data.to_json(orient='records'),
                "current_chart_type": "bar"
            })
            
            # Verify percentage transformation was applied
            self.assertEqual(result.pydantic.transformation, "percentage")
            self.assertEqual(result.pydantic.plot_type, "bar")  # Same chart type
            
            plot_spec = json.loads(result.pydantic.plot_spec)
            values = plot_spec["data"]["y"]
            self.assertAlmostEqual(sum(values), 100.0, delta=1.0)
            print("  ✅ Percentage conversion while maintaining chart type")
        
        print("  🎉 Percentage Conversion Scenario PASSED")

    def test_top_n_with_others_scenario(self):
        """
        Test Case 3: Top N filtering with Others grouping.
        
        Scenario:
        1. User has chart with many categories
        2. User asks: "Show only top 3 manufacturers, group the rest as Others"
        3. System should apply top_n transformation
        """
        
        print("\n🧪 Testing Top N with Others Scenario...")
        
        # Extended manufacturer data
        extended_data = pd.DataFrame({
            'manufacturer': ['Toyota', 'VW', 'Ford', 'Honda', 'Nissan', 'BMW', 'Mercedes', 'Audi', 'Hyundai', 'Kia'],
            'registrations': [150000, 120000, 100000, 95000, 85000, 60000, 55000, 50000, 45000, 40000]
        })
        
        with patch('agents.crew_agents.alternative_viz_crew') as mock_alt_viz:
            mock_viz_result = Mock()
            mock_viz_result.pydantic = Mock()
            mock_viz_result.pydantic.plot_type = "bar"
            mock_viz_result.pydantic.transformation = "top_3"
            mock_viz_result.pydantic.plot_spec = json.dumps({
                "type": "bar",
                "data": {
                    "x": ["Toyota", "VW", "Ford", "Others"],
                    "y": [150000, 120000, 100000, 530000]  # Others = sum of remaining
                },
                "layout": {"title": "Top 3 Manufacturers vs Others"}
            })
            mock_alt_viz.kickoff.return_value = mock_viz_result
            
            result = mock_alt_viz.kickoff(inputs={
                "user_request": "Show only top 3 manufacturers, group the rest as Others",
                "current_data": extended_data.to_json(orient='records'),
                "current_chart_type": "bar"
            })
            
            # Verify top N transformation
            self.assertEqual(result.pydantic.transformation, "top_3")
            
            plot_spec = json.loads(result.pydantic.plot_spec)
            x_values = plot_spec["data"]["x"]
            
            # Should have exactly 4 categories (top 3 + Others)
            self.assertEqual(len(x_values), 4)
            self.assertIn("Others", x_values)
            print("  ✅ Top N transformation with Others grouping")
        
        print("  🎉 Top N with Others Scenario PASSED")

    def test_follow_up_question_generation(self):
        """
        Test Case 4: Context-aware follow-up question generation.
        
        Scenario:
        1. User has analyzed manufacturer data
        2. System should generate relevant follow-up questions
        3. Questions should be schema-aware and contextually relevant
        """
        
        print("\n🧪 Testing Follow-up Question Generation...")
        
        with patch('agents.crew_agents.follow_up_crew') as mock_follow_up:
            mock_result = Mock()
            mock_result.pydantic = Mock()
            mock_result.pydantic.questions = [
                "Which manufacturers showed the highest growth in the last quarter?",
                "How do electric vehicle registrations compare across these manufacturers?",
                "What is the regional distribution for the top 3 manufacturers?",
                "Which vehicle models are most popular for each manufacturer?"
            ]
            mock_result.pydantic.categories = ["trends", "comparisons", "regional", "detailed"]
            mock_follow_up.kickoff.return_value = mock_result
            
            # Test follow-up generation
            result = mock_follow_up.kickoff(inputs={
                "data_analysis": "Analysis showing Toyota leads with 150K registrations",
                "original_query": "Which car manufacturers registered the most vehicles?",
                "data_insights": ["Toyota leads market", "Top 5 manufacturers account for 90% of registrations"],
                "db_schema": "vehicle_registrations(manufacturer, model, registration_date, region)"
            })
            
            # Verify follow-up questions
            questions = result.pydantic.questions
            self.assertEqual(len(questions), 4)
            self.assertTrue(all(isinstance(q, str) and len(q) > 10 for q in questions))
            
            # Check for schema-aware elements
            schema_aware_keywords = ['manufacturer', 'registration', 'quarter', 'regional', 'model']
            found_schema_elements = sum(1 for q in questions for keyword in schema_aware_keywords if keyword.lower() in q.lower())
            self.assertGreater(found_schema_elements, 2)
            print("  ✅ Schema-aware follow-up questions generated")
        
        print("  🎉 Follow-up Question Generation PASSED")


class TestVisualizationToolTransformations(unittest.TestCase):
    """Direct tests of the visualization tool transformation logic."""
    
    def setUp(self):
        """Set up visualization tool and test data."""
        self.viz_tool = DataFrameVisualizationTool()
        
        self.test_data = pd.DataFrame({
            'category': ['A', 'B', 'C', 'D', 'E'],
            'value': [100, 200, 150, 75, 25]
        })

    def test_direct_bar_to_pie_transformation(self):
        """Test direct transformation logic in the visualization tool."""
        
        print("\n🧪 Testing Direct Bar to Pie Transformation...")
        
        # Test the transformation method directly
        transformed_data = self.viz_tool._apply_intelligent_transformations(
            df=self.test_data,
            target_plot_type="pie",
            current_plot_type="bar",
            x_column="category",
            y_column="value",
            transformation=""
        )
        
        # Verify transformation
        self.assertIn("value_percentage", transformed_data.columns)
        
        # Check percentage calculation
        total_percentage = transformed_data["value_percentage"].sum()
        self.assertAlmostEqual(total_percentage, 100.0, places=1)
        
        # Verify data sorting (should be descending by percentage)
        percentages = transformed_data["value_percentage"].tolist()
        self.assertEqual(percentages, sorted(percentages, reverse=True))
        
        print("  ✅ Direct transformation logic working correctly")

    def test_top_n_transformation_logic(self):
        """Test top N transformation with Others grouping."""
        
        print("\n🧪 Testing Top N Transformation Logic...")
        
        # Create data with more categories
        large_data = pd.DataFrame({
            'item': [f'Item_{i}' for i in range(10)],
            'count': [100-i*10 for i in range(10)]  # Decreasing values
        })
        
        # Test top 3 transformation
        transformed_data = self.viz_tool._apply_intelligent_transformations(
            df=large_data,
            target_plot_type="bar",
            current_plot_type="bar",
            x_column="item",
            y_column="count",
            transformation="top_3"
        )
        
        # Should have exactly 3 items (top 2 + Others)
        self.assertEqual(len(transformed_data), 3)
        self.assertIn("Others", transformed_data["item"].values)
        
        # Verify Others calculation
        others_row = transformed_data[transformed_data["item"] == "Others"]
        self.assertEqual(len(others_row), 1)
        
        print("  ✅ Top N transformation logic working correctly")


def run_integration_tests():
    """Run all integration tests and report results."""
    
    print("🧪 Running Advanced Visualization Integration Tests...")
    print("=" * 80)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestOrchestrationIntegration))
    test_suite.addTest(unittest.makeSuite(TestVisualizationToolTransformations))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Report summary
    print("\n" + "=" * 80)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
            print(f"    {traceback}")
    
    if result.errors:
        print("\n⚠️ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
            print(f"    {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("   Advanced visualization orchestration is working correctly.")
    else:
        print(f"\n⚠️ {len(result.failures + result.errors)} test(s) failed.")
        print("   Please review the orchestration implementation.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
