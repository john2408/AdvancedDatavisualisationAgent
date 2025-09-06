#!/usr/bin/env python3
"""
Quick evaluation test - just tests the scoring logic without running the full pipeline.
"""

import os
import sys
import json

# Add the project root to Python path
sys.path.append('/Users/JOHTORR/Repos/AdvancedDatavisualisationAgent')

def test_scoring_logic():
    """Test the scoring logic against known data."""
    print("🧪 Testing Scoring Logic")
    print("=" * 40)
    
    # Load actual test results
    with open('/Users/JOHTORR/Repos/AdvancedDatavisualisationAgent/tests/test_data/generated/complete_test_data.json', 'r') as f:
        test_data = json.load(f)
    
    # Test scoring for a few questions
    test_cases = [
        {
            "name": "Question 6 - Top 5 brands",
            "expected": test_data["Question6"],
            "actual": {"rows": 5, "columns": ["oem_name", "total_registrations"]}
        },
        {
            "name": "Question 7 - Monthly totals", 
            "expected": test_data["Question7"],
            "actual": {"rows": 24, "columns": ["year_month", "total_registrations"]}
        },
        {
            "name": "Question 14 - Top 3 body types",
            "expected": test_data["Question14"], 
            "actual": {"rows": 3, "columns": ["body_type", "total_registered"]}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        
        expected = test_case["expected"]
        actual = test_case["actual"]
        
        expected_rows = expected.get("Rows", 0)
        expected_columns = expected.get("Columns", [])
        expected_columns_count = len(expected_columns) if expected_columns else 0
        
        actual_rows = actual["rows"]
        actual_columns = actual["columns"]
        actual_columns_count = len(actual_columns)
        
        # Calculate scores
        rows_score = 50 if actual_rows == expected_rows else 0
        columns_count_score = 40 if actual_columns_count == expected_columns_count else 0
        column_names_score = 10 if set(actual_columns) == set(expected_columns) else 0
        total_score = rows_score + columns_count_score + column_names_score
        
        print(f"   Expected: {expected_rows} rows, {expected_columns_count} columns {expected_columns}")
        print(f"   Actual:   {actual_rows} rows, {actual_columns_count} columns {actual_columns}")
        print(f"   Scores: Rows: {rows_score}/50, Columns: {columns_count_score}/40, Names: {column_names_score}/10")
        print(f"   Total: {total_score}/100 ({'✅ PASS' if total_score == 100 else '❌ FAIL'})")

def show_test_data_summary():
    """Show a summary of the test data."""
    print("\n📊 Test Data Summary")
    print("=" * 40)
    
    with open('/Users/JOHTORR/Repos/AdvancedDatavisualisationAgent/tests/test_data/generated/complete_test_data.json', 'r') as f:
        test_data = json.load(f)
    
    successful_questions = 0
    total_questions = 0
    
    for key, value in test_data.items():
        if key.startswith("Question") and key != "_metadata":
            total_questions += 1
            if value.get("Success", False):
                successful_questions += 1
                print(f"✅ {key}: {value.get('Rows', 0)} rows, {len(value.get('Columns', []))} columns")
            else:
                print(f"❌ {key}: Failed - {value.get('Error', 'Unknown error')}")
    
    print(f"\n📈 Summary: {successful_questions}/{total_questions} questions have valid test data")
    
    if "_metadata" in test_data:
        metadata = test_data["_metadata"]
        print(f"📋 Total Questions: {metadata.get('total_questions', 0)}")
        print(f"✅ Successful: {metadata.get('successful_questions', 0)}")
        print(f"❌ Failed: {metadata.get('failed_questions', 0)}")

def main():
    """Main function."""
    print("🚀 Quick Evaluation Test")
    print("=" * 50)
    
    try:
        show_test_data_summary()
        test_scoring_logic()
        
        print(f"\n✅ Evaluation logic test complete!")
        print(f"📁 Full evaluation can be run with: python tests/test_evaluate_sql_agent_accuracy.py")
        
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
