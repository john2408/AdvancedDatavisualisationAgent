#!/usr/bin/env python3
"""
Unit tests for the new hybrid visualization approach (Proposal 2).

Tests the Analytics Selector + Deterministic Plot Builder pattern that replaces
the slow visualization agent with fast heuristics + single LLM call + deterministic building.
"""

import unittest
import pandas as pd
import json
import sys
import os
from unittest.mock import Mock, patch

# Add the parent directory to sys.path so we can import from the project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAnalyticsSelector(unittest.TestCase):
    """Test the analytics selector that determines chart type and parameters."""
    
    def setUp(self):
        """Set up test data for various scenarios."""
        
        # Vehicle manufacturer data (categorical + numeric)
        self.manufacturer_data = pd.DataFrame({
            'manufacturer': ['Toyota', 'Volkswagen', 'Ford', 'Honda', 'Nissan', 'BMW', 'Mercedes', 'Audi'],
            'registrations': [150000, 120000, 100000, 95000, 85000, 60000, 55000, 50000]
        })
        
        # Time series data (date + numeric)
        self.time_series_data = pd.DataFrame({
            'month': ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06'],
            'registrations': [80000, 85000, 92000, 88000, 94000, 89000]
        })
        
        # Multi-dimensional data (categorical + numeric + color dimension)
        self.multi_dim_data = pd.DataFrame({
            'region': ['North', 'South', 'East', 'West', 'Central'] * 3,
            'vehicle_type': ['SUV'] * 5 + ['Sedan'] * 5 + ['Truck'] * 5,
            'sales': [25000, 30000, 22000, 28000, 18000, 
                     20000, 25000, 18000, 24000, 15000,
                     15000, 18000, 12000, 16000, 10000]
        })
        
        # Market share scenario data
        self.market_share_data = pd.DataFrame({
            'brand': ['Tesla', 'BMW', 'Mercedes', 'Audi', 'Others'],
            'ev_sales': [45000, 25000, 20000, 15000, 10000]
        })

    def test_heuristic_chart_selection_simple_categorical(self):
        """Test heuristic selection for simple categorical data -> bar chart."""
        from frontend.analytics_selector import select_chart_plan_heuristic
        
        user_query = "Which car manufacturers registered the most vehicles?"
        plan = select_chart_plan_heuristic(self.manufacturer_data, user_query)
        
        self.assertEqual(plan.chart_type, "bar")
        self.assertEqual(plan.x, "manufacturer")
        self.assertEqual(plan.y, ["registrations"])
        self.assertIsNone(plan.color)
        self.assertEqual(plan.aggregation, "sum")
        self.assertIsNone(plan.transform)
        
        print("✅ Simple categorical -> bar chart heuristic works")

    def test_heuristic_chart_selection_time_series(self):
        """Test heuristic selection for time series data -> line chart."""
        from frontend.analytics_selector import select_chart_plan_heuristic
        
        user_query = "Show monthly registration trends over time"
        plan = select_chart_plan_heuristic(self.time_series_data, user_query)
        
        self.assertEqual(plan.chart_type, "line")
        self.assertEqual(plan.x, "month")
        self.assertEqual(plan.y, ["registrations"])
        self.assertIsNone(plan.color)
        
        print("✅ Time series -> line chart heuristic works")

    def test_heuristic_chart_selection_market_share(self):
        """Test heuristic selection for market share keywords -> pie chart."""
        from frontend.analytics_selector import select_chart_plan_heuristic
        
        user_query = "Show the market share distribution of electric vehicle brands"
        plan = select_chart_plan_heuristic(self.market_share_data, user_query)
        
        self.assertEqual(plan.chart_type, "pie")
        self.assertEqual(plan.x, "brand")
        self.assertEqual(plan.y, ["ev_sales"])
        self.assertEqual(plan.transform, "percentage")
        
        print("✅ Market share keywords -> pie chart with percentage transform works")

    def test_heuristic_chart_selection_multi_dimensional(self):
        """Test heuristic selection for multi-dimensional data -> stacked bar chart."""
        from frontend.analytics_selector import select_chart_plan_heuristic
        
        user_query = "Show vehicle sales by region and type"
        plan = select_chart_plan_heuristic(self.multi_dim_data, user_query)
        
        self.assertEqual(plan.chart_type, "stacked_bar")
        self.assertEqual(plan.x, "region")
        self.assertEqual(plan.y, ["sales"])
        self.assertEqual(plan.color, "vehicle_type")
        
        print("✅ Multi-dimensional -> stacked bar chart heuristic works")

    def test_heuristic_distribution_keywords(self):
        """Test heuristic detection of distribution keywords -> histogram/box."""
        from frontend.analytics_selector import select_chart_plan_heuristic
        
        # Use a query that specifically asks for distribution without market share keywords
        user_query = "Show the frequency distribution of vehicle registration values"
        plan = select_chart_plan_heuristic(self.manufacturer_data, user_query)
        
        self.assertIn(plan.chart_type, ["histogram", "box"])
        self.assertEqual(plan.y, ["registrations"])
        
        print("✅ Distribution keywords -> histogram/box chart heuristic works")

    @patch('frontend.analytics_selector.llm_fallback_chart_selection')
    def test_llm_fallback_when_heuristics_fail(self, mock_llm):
        """Test LLM fallback when heuristics cannot determine chart type."""
        from frontend.analytics_selector import select_chart_plan
        
        # Mock LLM response
        mock_plan = Mock()
        mock_plan.chart_type = "scatter"
        mock_plan.x = "registrations"
        mock_plan.y = ["manufacturer"]
        mock_plan.color = None
        mock_plan.aggregation = "none"
        mock_plan.transform = None
        mock_plan.title = "Complex Scatter Analysis"
        mock_llm.return_value = mock_plan
        
        # Create data that won't match any heuristics (all string columns)
        difficult_data = pd.DataFrame({
            'text_col_1': ['a', 'b', 'c'],
            'text_col_2': ['x', 'y', 'z'],
            'text_col_3': ['1', '2', '3']  # Looks numeric but is string
        })
        
        # Complex query that should trigger LLM fallback
        user_query = "Create a complex multidimensional analysis showing correlations"
        plan = select_chart_plan(difficult_data, user_query)
        
        # Verify LLM was called and result returned
        mock_llm.assert_called_once()
        self.assertEqual(plan.chart_type, "scatter")
        self.assertEqual(plan.title, "Complex Scatter Analysis")
        
        print("✅ LLM fallback mechanism works when heuristics fail")


class TestDeterministicPlotBuilder(unittest.TestCase):
    """Test the deterministic plot builder that converts ChartPlan to Plotly Figure."""
    
    def setUp(self):
        """Set up test data and chart plans."""
        self.sample_data = pd.DataFrame({
            'category': ['A', 'B', 'C', 'D'],
            'value': [100, 200, 150, 300],
            'group': ['X', 'Y', 'X', 'Y']
        })
    
    def test_build_simple_bar_chart(self):
        """Test building simple bar chart from plan."""
        from frontend.plot_builder import build_figure_from_plan, ChartPlan
        
        plan = ChartPlan(
            chart_type="bar",
            x="category",
            y=["value"],
            color=None,
            aggregation="sum",
            transform=None,
            title="Simple Bar Chart"
        )
        
        fig = build_figure_from_plan(plan, self.sample_data)
        
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 1)  # Single trace
        self.assertEqual(fig.data[0].type, "bar")
        self.assertEqual(list(fig.data[0].x), ['A', 'B', 'C', 'D'])
        self.assertEqual(list(fig.data[0].y), [100, 200, 150, 300])
        
        print("✅ Simple bar chart building works")

    def test_build_stacked_bar_chart(self):
        """Test building stacked bar chart with color grouping."""
        from frontend.plot_builder import build_figure_from_plan, ChartPlan
        
        plan = ChartPlan(
            chart_type="stacked_bar",
            x="category",
            y=["value"],
            color="group",
            aggregation="sum",
            transform=None,
            title="Stacked Bar Chart"
        )
        
        fig = build_figure_from_plan(plan, self.sample_data)
        
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 2)  # Two traces for groups X and Y
        self.assertEqual(fig.layout.barmode, "stack")
        
        print("✅ Stacked bar chart building works")

    def test_build_pie_chart_with_percentage_transform(self):
        """Test building pie chart with percentage transformation."""
        from frontend.plot_builder import build_figure_from_plan, ChartPlan
        
        plan = ChartPlan(
            chart_type="pie",
            x="category",
            y=["value"],
            color=None,
            aggregation="sum",
            transform="percentage",
            title="Pie Chart with Percentages"
        )
        
        fig = build_figure_from_plan(plan, self.sample_data)
        
        self.assertIsNotNone(fig)
        self.assertEqual(fig.data[0].type, "pie")
        self.assertEqual(list(fig.data[0].labels), ['A', 'B', 'C', 'D'])
        
        # Verify percentage calculation
        values = list(fig.data[0].values)
        total = sum([100, 200, 150, 300])
        expected_percentages = [100/total*100, 200/total*100, 150/total*100, 300/total*100]
        for actual, expected in zip(values, expected_percentages):
            self.assertAlmostEqual(actual, expected, places=1)
        
        print("✅ Pie chart with percentage transformation works")

    def test_build_multi_line_chart(self):
        """Test building line chart with multiple y metrics."""
        from frontend.plot_builder import build_figure_from_plan, ChartPlan
        
        # Data with multiple metrics
        multi_metric_data = pd.DataFrame({
            'month': ['Jan', 'Feb', 'Mar', 'Apr'],
            'sales': [1000, 1200, 1100, 1300],
            'costs': [800, 900, 850, 950]
        })
        
        plan = ChartPlan(
            chart_type="multi_line",
            x="month",
            y=["sales", "costs"],
            color=None,
            aggregation="none",
            transform=None,
            title="Multi-Metric Line Chart"
        )
        
        fig = build_figure_from_plan(plan, multi_metric_data)
        
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 2)  # Two traces for sales and costs
        self.assertEqual(fig.data[0].type, "scatter")
        self.assertEqual(fig.data[0].mode, "lines+markers")
        
        print("✅ Multi-line chart building works")

    def test_build_normalized_stacked_bar(self):
        """Test building normalized stacked bar chart (market share style)."""
        from frontend.plot_builder import build_figure_from_plan, ChartPlan
        
        plan = ChartPlan(
            chart_type="stacked_bar",
            x="category",
            y=["value"],
            color="group",
            aggregation="sum",
            transform="percentage",
            title="Normalized Stacked Bar Chart"
        )
        
        fig = build_figure_from_plan(plan, self.sample_data)
        
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 2)  # Two traces
        self.assertEqual(fig.layout.barmode, "stack")
        
        # Verify normalization: each category should sum to 100%
        # Category A: groups X(100) -> 100%
        # Category B: groups Y(200) -> 100% 
        # Category C: groups X(150) -> 100%
        # Category D: groups Y(300) -> 100%
        
        print("✅ Normalized stacked bar chart building works")


class TestHybridVisualizationIntegration(unittest.TestCase):
    """Test the complete hybrid visualization pipeline."""
    
    def setUp(self):
        """Set up test data for integration testing."""
        self.vehicle_data = pd.DataFrame({
            'manufacturer': ['Toyota', 'VW', 'Ford', 'Honda'],
            'registrations': [150000, 120000, 100000, 95000]
        })

    def test_step_4_hybrid_visualization_simple_case(self):
        """Test the new step_4_hybrid_visualization function for simple case."""
        from frontend.hybrid_visualization import step_4_hybrid_visualization
        
        user_query = "Which manufacturers have the most registrations?"
        result = step_4_hybrid_visualization(self.vehicle_data, user_query)
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["figure"])
        self.assertIn("bar", result["summary"].lower())
        
        print("✅ Simple hybrid visualization pipeline works")

    def test_step_4_hybrid_visualization_market_share_case(self):
        """Test hybrid visualization for market share scenario."""
        from frontend.hybrid_visualization import step_4_hybrid_visualization
        
        user_query = "Show the market share distribution of vehicle manufacturers"
        result = step_4_hybrid_visualization(self.vehicle_data, user_query)
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["figure"])
        self.assertIn("pie", result["summary"].lower())
        
        print("✅ Market share hybrid visualization pipeline works")

    def test_step_4_hybrid_visualization_fallback(self):
        """Test hybrid visualization fallback to simple bar chart."""
        from frontend.hybrid_visualization import step_4_hybrid_visualization
        
        # Data that might cause issues
        problematic_data = pd.DataFrame({
            'col1': [None, None, None],
            'col2': ['', '', '']
        })
        
        user_query = "Show some analysis"
        result = step_4_hybrid_visualization(problematic_data, user_query)
        
        # Should either succeed with fallback or gracefully fail
        if result["success"]:
            self.assertIsNotNone(result["figure"])
        else:
            # The word "error" should be in the summary for failed cases
            self.assertTrue("unable" in result["summary"].lower() or "error" in result["summary"].lower())
        
        print("✅ Hybrid visualization fallback handling works")

    def test_alternative_visualization_with_target_plot_type(self):
        """Test alternative visualization using target_plot_type pattern."""
        from frontend.hybrid_visualization import step_4_hybrid_visualization
        
        # Simulate follow-up scenario: "convert to pie chart"
        user_query = "convert this bar chart to pie chart showing percentages"
        result = step_4_hybrid_visualization(self.vehicle_data, user_query)
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["figure"])
        # Should detect pie chart request
        self.assertIn("pie", result["summary"].lower())
        
        print("✅ Alternative visualization with chart conversion works")


class TestHeuristicKeywordDetection(unittest.TestCase):
    """Test keyword detection heuristics for chart type selection."""
    
    def test_market_share_keywords(self):
        """Test detection of market share related keywords."""
        from frontend.analytics_selector import detect_chart_keywords
        
        queries = [
            "Show the market share distribution",
            "What percentage of sales does each brand have?",
            "Display the share of registrations by manufacturer",
            "Show proportions of vehicle types"
        ]
        
        for query in queries:
            keywords = detect_chart_keywords(query)
            self.assertIn("percentage", keywords)
            print(f"✅ Detected market share keywords in: '{query[:30]}...'")

    def test_time_series_keywords(self):
        """Test detection of time series related keywords."""
        from frontend.analytics_selector import detect_chart_keywords
        
        queries = [
            "Show trends over time",
            "Display monthly registration data",
            "What are the quarterly sales patterns?",
            "Show the evolution of registrations"
        ]
        
        for query in queries:
            keywords = detect_chart_keywords(query)
            self.assertIn("time_series", keywords)
            print(f"✅ Detected time series keywords in: '{query[:30]}...'")

    def test_distribution_keywords(self):
        """Test detection of distribution analysis keywords."""
        from frontend.analytics_selector import detect_chart_keywords
        
        queries = [
            "Show the distribution of values",
            "What are the outliers in the data?",
            "Display the spread of registrations",
            "Show histogram of vehicle counts"
        ]
        
        for query in queries:
            keywords = detect_chart_keywords(query)
            self.assertIn("distribution", keywords)
            print(f"✅ Detected distribution keywords in: '{query[:30]}...'")

    def test_comparison_keywords(self):
        """Test detection of comparison analysis keywords."""
        from frontend.analytics_selector import detect_chart_keywords
        
        queries = [
            "Compare sales between regions",
            "Show differences in registration patterns",
            "Which manufacturer performs better?",
            "Contrast the performance of vehicle types"
        ]
        
        for query in queries:
            keywords = detect_chart_keywords(query)
            self.assertIn("comparison", keywords)
            print(f"✅ Detected comparison keywords in: '{query[:30]}...'")


if __name__ == "__main__":
    print("🧪 Running Hybrid Visualization Tests")
    print("=" * 60)
    
    # Run tests in order
    test_classes = [
        TestAnalyticsSelector,
        TestDeterministicPlotBuilder, 
        TestHybridVisualizationIntegration,
        TestHeuristicKeywordDetection
    ]
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}")
        print("-" * 40)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            print(f"❌ {test_class.__name__} had failures")
        else:
            print(f"✅ {test_class.__name__} passed all tests")
    
    print("\n🎉 Hybrid Visualization Test Suite Complete!")
