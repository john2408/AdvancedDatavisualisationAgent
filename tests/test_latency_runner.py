#!/usr/bin/env python3
"""
Quick test runner for the App Latency Evaluation system.
"""

import os
import sys
import time

# Add the project root to Python path
sys.path.append('/Users/JOHTORR/Repos/AdvancedDatavisualisationAgent')

def test_latency_evaluation():
    """Test the latency evaluation with a single question."""
    print("🧪 Testing App Latency Evaluation System")
    print("=" * 50)
    
    try:
        from tests.test_evaluation_app_latency import AppLatencyEvaluator
        
        evaluator = AppLatencyEvaluator()
        
        # Test with just one question
        print("📋 Testing with first question only...")
        
        # Test single question evaluation
        test_question = "What are the top 5 car brands by total registrations in 2024?"
        result = evaluator.evaluate_pipeline_for_question(1, test_question)
        
        print(f"\n📊 Test Results:")
        print(f"   Question: {result.question}")
        print(f"   Success: {result.success}")
        print(f"   Total Duration: {result.total_duration:.2f}s")
        print(f"   Steps Completed: {len(result.step_timings)}")
        
        for timing in result.step_timings:
            status = "✅" if timing.success else "❌"
            print(f"   {status} {timing.step_name}: {timing.duration_seconds:.2f}s")
        
        # Test statistics calculation
        evaluator.results = [result]
        summary = evaluator.calculate_summary_statistics()
        
        print(f"\n📈 Statistics Test:")
        print(f"   Pipeline Mean: {summary['total_pipeline']['mean']:.2f}s")
        print(f"   Steps Available: {list(summary['steps'].keys())}")
        
        # Test markdown generation
        evaluation_results = {
            "summary": summary,
            "results": [result],
            "metadata": {
                "evaluation_start": "2025-09-06T16:00:00",
                "evaluation_end": "2025-09-06T16:01:00",
                "total_duration_seconds": 60.0,
                "questions_evaluated": 1,
                "successful_pipelines": 1 if result.success else 0,
                "failed_pipelines": 0 if result.success else 1
            }
        }
        
        report_path = evaluator.generate_markdown_report(evaluation_results)
        print(f"\n📄 Report generated: {report_path}")
        
        return True
        
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("🚀 App Latency Evaluation Quick Test")
    print("=" * 50)
    
    success = test_latency_evaluation()
    
    if success:
        print(f"\n✅ Quick test passed!")
        print(f"📋 Full evaluation can be run with:")
        print(f"   python tests/test_evaluation_app_latency.py --max-questions 3")
        print(f"   python tests/test_evaluation_app_latency.py  # For all 24 questions")
    else:
        print(f"\n❌ Quick test failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
