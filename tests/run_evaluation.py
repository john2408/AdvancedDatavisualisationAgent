#!/usr/bin/env python3
"""
Command line runner for SQL Agent Accuracy Evaluation
"""

import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Evaluate SQL Agent Accuracy against Expected Results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test first 3 questions only
  python run_evaluation.py --max-questions 3
  
  # Run full evaluation (all 24 questions)
  python run_evaluation.py
  
  # Run evaluation without saving results
  python run_evaluation.py --no-save
  
  # Quick test of scoring logic only
  python run_evaluation.py --quick-test
        """
    )
    
    parser.add_argument(
        '--max-questions', 
        type=int, 
        help='Maximum number of questions to evaluate (default: all 24)'
    )
    
    parser.add_argument(
        '--no-save', 
        action='store_true', 
        help='Do not save results to file'
    )
    
    parser.add_argument(
        '--quick-test', 
        action='store_true', 
        help='Run quick test of scoring logic only (no SQL generation)'
    )
    
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='tests/test_data/evaluation_results',
        help='Directory to save evaluation results (default: tests/test_data/evaluation_results)'
    )
    
    args = parser.parse_args()
    
    print("🚀 SQL Agent Accuracy Evaluation")
    print("=" * 50)
    
    if args.quick_test:
        print("Running quick test of scoring logic...")
        exec(open('quick_eval_test.py').read())
        return
    
    try:
        from tests.test_evaluate_sql_agent_accuracy import run_evaluation
        
        print(f"📋 Max Questions: {args.max_questions or 'All (24)'}")
        print(f"💾 Save Results: {not args.no_save}")
        
        if args.max_questions:
            print(f"⚠️  Running limited evaluation ({args.max_questions} questions)")
        
        # Run the evaluation
        result_path = run_evaluation(
            max_questions=args.max_questions,
            save_results=not args.no_save
        )
        
        if not args.no_save:
            print(f"\n🎉 Evaluation complete!")
            print(f"📁 Results saved to: {result_path}")
        else:
            print(f"\n🎉 Evaluation complete!")
        
    except KeyboardInterrupt:
        print("\n🛑 Evaluation interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n💥 Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
