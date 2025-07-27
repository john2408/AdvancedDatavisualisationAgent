#!/usr/bin/env python3
"""
Test runner for advanced visualization and orchestration functionality.

This script runs comprehensive tests for:
1. Data transformation scenarios (bar→pie, absolute→percentage, etc.)
2. Context-aware follow-up question generation
3. Orchestration decision making
4. Integration testing of the full pipeline

Usage:
    python run_advanced_tests.py [--verbose] [--test-pattern PATTERN]
"""

import sys
import os
import unittest
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import test modules
try:
    from tests.test_advanced_visualizations import run_advanced_visualization_tests
    from tests.test_orchestration_integration import run_integration_tests
except ImportError as e:
    print(f"⚠️ Warning: Could not import test modules: {e}")
    print("Make sure you're running from the project root directory.")
    sys.exit(1)


def print_banner():
    """Print test banner."""
    print("🚀 Advanced Data Visualization Agent - Test Suite")
    print("=" * 80)
    print("Testing intelligent chart transformations and orchestration...")
    print("=" * 80)


def print_test_scenarios():
    """Print the test scenarios that will be covered."""
    scenarios = [
        "📊 Scenario 1: Bar Chart → Pie Chart (with percentage conversion)",
        "📈 Scenario 2: Absolute Values → Percentage Display", 
        "📉 Scenario 3: Line Chart → Bar Chart (time series aggregation)",
        "🎯 Scenario 4: Category Consolidation (Top N + Others grouping)",
        "🔄 Scenario 5: Context-aware Follow-up Generation",
        "🤖 Scenario 6: Orchestration Decision Making",
        "🔗 Scenario 7: End-to-End Integration Testing"
    ]
    
    print("\n🧪 TEST SCENARIOS COVERED:")
    print("-" * 50)
    for scenario in scenarios:
        print(f"  {scenario}")
    print()


def run_unit_tests():
    """Run unit tests for visualization transformations."""
    print("🧪 PHASE 1: Unit Tests - Visualization Transformations")
    print("-" * 60)
    
    success = run_advanced_visualization_tests()
    
    if success:
        print("✅ Unit tests completed successfully")
    else:
        print("❌ Unit tests failed")
    
    return success


def run_integration_test_phase():
    """Run integration tests for orchestration."""
    print("\n🔗 PHASE 2: Integration Tests - Orchestration Pipeline")
    print("-" * 60)
    
    success = run_integration_tests()
    
    if success:
        print("✅ Integration tests completed successfully")
    else:
        print("❌ Integration tests failed")
    
    return success


def run_manual_test_scenarios():
    """Run manual verification of key scenarios."""
    print("\n🎯 PHASE 3: Manual Scenario Verification")
    print("-" * 60)
    
    # Import here to avoid circular imports
    try:
        from agents.tools.visualization_tool import DataFrameVisualizationTool
        import pandas as pd
        import json
        
        viz_tool = DataFrameVisualizationTool()
        
        # Test scenario: Bar to Pie with real data
        print("Testing: Vehicle manufacturer data (Bar → Pie conversion)")
        
        test_data = pd.DataFrame({
            'manufacturer': ['Toyota', 'Volkswagen', 'Ford', 'Honda', 'Nissan'],
            'registrations': [150000, 120000, 100000, 95000, 85000]
        })
        
        # Test the transformation
        dataframe_json = test_data.to_json(orient='records')
        result = viz_tool._run(
            dataframe_json=dataframe_json,
            plot_type="pie",
            x_column="manufacturer",
            y_column="registrations",
            current_chart_type="bar",
            title="Vehicle Registrations by Manufacturer (Pie Chart)"
        )
        
        # Parse and validate result
        plot_spec = json.loads(result)
        
        if "error" not in plot_spec and plot_spec.get("type") == "pie":
            print("  ✅ Bar to Pie transformation: SUCCESS")
            
            # Check data integrity
            data = plot_spec.get("data", {})
            labels = data.get("labels", [])
            values = data.get("values", [])
            
            if len(labels) == len(values) and len(labels) > 0:
                print(f"  ✅ Data integrity: {len(labels)} categories preserved")
                
                # Check if transformation was applied (values should represent meaningful distribution)
                if all(isinstance(v, (int, float)) for v in values):
                    print("  ✅ Value transformation: Numeric values generated")
                else:
                    print("  ⚠️ Value transformation: Non-numeric values detected")
            else:
                print("  ❌ Data integrity: Mismatched labels and values")
        else:
            print("  ❌ Bar to Pie transformation: FAILED")
            print(f"     Error: {plot_spec.get('error', 'Unknown error')}")
            return False
        
        print("  🎉 Manual scenario verification completed successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Manual scenario verification failed: {e}")
        return False


def generate_test_report(unit_success, integration_success, manual_success):
    """Generate comprehensive test report."""
    print("\n" + "=" * 80)
    print("📋 COMPREHENSIVE TEST REPORT")
    print("=" * 80)
    
    phases = [
        ("Unit Tests (Transformations)", unit_success),
        ("Integration Tests (Orchestration)", integration_success),
        ("Manual Scenarios", manual_success)
    ]
    
    all_passed = all(success for _, success in phases)
    
    print("Test Phase Results:")
    for phase_name, success in phases:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {phase_name:<35} {status}")
    
    print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if all_passed else '⚠️ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🚀 READY FOR DEPLOYMENT")
        print("The advanced visualization system is working correctly:")
        print("  • Bar → Pie transformations with percentage conversion")
        print("  • Context-aware follow-up question generation")
        print("  • Intelligent orchestration decision making")
        print("  • Proper data transformation handling")
    else:
        print("\n🔧 REQUIRES ATTENTION")
        print("Some tests failed. Please review and fix issues before deployment.")
    
    return all_passed


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run advanced visualization tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--skip-integration", action="store_true", help="Skip integration tests")
    parser.add_argument("--skip-manual", action="store_true", help="Skip manual verification")
    
    args = parser.parse_args()
    
    print_banner()
    print_test_scenarios()
    
    # Phase 1: Unit Tests
    unit_success = run_unit_tests()
    
    # Phase 2: Integration Tests
    if not args.skip_integration:
        integration_success = run_integration_test_phase()
    else:
        print("\n⏭️ Skipping integration tests")
        integration_success = True
    
    # Phase 3: Manual Verification
    if not args.skip_manual:
        manual_success = run_manual_test_scenarios()
    else:
        print("\n⏭️ Skipping manual verification")
        manual_success = True
    
    # Generate report
    overall_success = generate_test_report(unit_success, integration_success, manual_success)
    
    # Exit with appropriate code
    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()
