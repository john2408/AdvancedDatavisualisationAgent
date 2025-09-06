#!/usr/bin/env python3
"""
Test to evaluate SQL agent accuracy by comparing generated results with expected results.
"""

import os
import sys
import json
import pandas as pd
import pytest
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Add the project root to Python path
sys.path.append('/Users/JOHTORR/Repos/AdvancedDatavisualisationAgent')

from agents.crew_agents import sql_generator_crew, sql_reviewer_crew
from backend.sql_utils import run_query
from omegaconf import OmegaConf
from tests.test_data.sample_sql_questions import test_questions

# Load configuration
config = OmegaConf.load("config.yaml")
DB_PATH = config.db_path
db_schema_agent = config.db_schema_agent

# Load expected results
EXPECTED_RESULTS_PATH = "tests/test_data/generated/complete_test_data.json"

class SQLAgentEvaluator:
    """Evaluates SQL agent accuracy against expected results."""
    
    def __init__(self):
        """Initialize the evaluator."""
        self.expected_results = self._load_expected_results()
        self.scoring_results = {}
        
    def _load_expected_results(self) -> Dict:
        """Load expected results from JSON file."""
        with open(EXPECTED_RESULTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _execute_sql_pipeline(self, question: str) -> Dict[str, Any]:
        """Execute the 3-step SQL generation and execution pipeline."""
        try:
            # Step 1: Generate SQL
            print("📝 Generating SQL...")
            gen_output = sql_generator_crew.kickoff(inputs={
                "user_input": question, 
                "db_schema": db_schema_agent
            })
            initial_sql = gen_output.pydantic.sqlquery
            print("✅ Generated SQL")
            
            # Step 2: Review SQL
            print("🔍 Reviewing SQL...")
            review_output = sql_reviewer_crew.kickoff(inputs={
                "sql_query": initial_sql, 
                "db_schema": db_schema_agent
            })
            final_sql = review_output.pydantic.reviewed_sqlquery
            print("✅ Final SQL ready")
            
            # Step 3: Execute query
            print("⚡ Executing query...")
            query_result = run_query(final_sql, DB_PATH)
            
            if query_result is not None and isinstance(query_result, pd.DataFrame) and not query_result.empty:
                if "Error" not in query_result.columns:
                    return {
                        "success": True,
                        "initial_sql": initial_sql,
                        "final_sql": final_sql,
                        "dataframe": query_result,
                        "rows": len(query_result),
                        "columns": list(query_result.columns),
                        "error": None
                    }
                else:
                    error_msg = query_result["Error"].iloc[0]
                    return {
                        "success": False,
                        "error": f"Query execution failed: {error_msg}",
                        "final_sql": final_sql
                    }
            else:
                return {
                    "success": False,
                    "error": "No data returned",
                    "final_sql": final_sql
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Pipeline failed: {str(e)}"
            }
    
    def _compare_results(self, actual: Dict, expected: Dict) -> Dict[str, Any]:
        """Compare actual results with expected results and calculate score."""
        score_breakdown = {
            "rows_match": False,
            "columns_count_match": False,
            "column_names_match": False,
            "rows_score": 0,
            "columns_count_score": 0,
            "column_names_score": 0,
            "total_score": 0
        }
        
        if not actual["success"]:
            return {
                **score_breakdown,
                "error": actual.get("error", "Unknown error"),
                "comparison_possible": False
            }
        
        expected_rows = expected.get("Rows", 0)
        expected_columns = expected.get("Columns", [])
        expected_columns_count = len(expected_columns) if expected_columns else 0
        
        actual_rows = actual["rows"]
        actual_columns = actual["columns"]
        actual_columns_count = len(actual_columns)
        
        # Check rows match (50 points)
        if actual_rows == expected_rows:
            score_breakdown["rows_match"] = True
            score_breakdown["rows_score"] = 50
        
        # Check columns count match (40 points)
        if actual_columns_count == expected_columns_count:
            score_breakdown["columns_count_match"] = True
            score_breakdown["columns_count_score"] = 40
        
        # Check column names match (10 points)
        if set(actual_columns) == set(expected_columns):
            score_breakdown["column_names_match"] = True
            score_breakdown["column_names_score"] = 10
        
        # Calculate total score
        score_breakdown["total_score"] = (
            score_breakdown["rows_score"] + 
            score_breakdown["columns_count_score"] + 
            score_breakdown["column_names_score"]
        )
        
        return {
            **score_breakdown,
            "comparison_possible": True,
            "expected_rows": expected_rows,
            "actual_rows": actual_rows,
            "expected_columns": expected_columns,
            "actual_columns": actual_columns,
            "expected_columns_count": expected_columns_count,
            "actual_columns_count": actual_columns_count
        }
    
    def evaluate_question(self, question_num: int, question: str) -> Dict[str, Any]:
        """Evaluate a single question."""
        print(f"\n🔄 Evaluating Question {question_num}: {question}")
        print("-" * 80)
        
        # Get expected results
        expected_key = f"Question{question_num}"
        if expected_key not in self.expected_results:
            return {
                "question_num": question_num,
                "question": question,
                "error": f"No expected results found for {expected_key}",
                "score": 0
            }
        
        expected = self.expected_results[expected_key]
        
        # Execute SQL pipeline
        actual = self._execute_sql_pipeline(question)
        
        # Compare results
        comparison = self._compare_results(actual, expected)
        
        # Create evaluation result
        result = {
            "question_num": question_num,
            "question": question,
            "expected": {
                "rows": expected.get("Rows", 0),
                "columns": expected.get("Columns", []),
                "columns_count": len(expected.get("Columns", []))
            },
            "actual": {
                "success": actual["success"],
                "rows": actual.get("rows", 0),
                "columns": actual.get("columns", []),
                "columns_count": len(actual.get("columns", [])),
                "error": actual.get("error")
            },
            "comparison": comparison,
            "score": comparison.get("total_score", 0),
            "max_score": 100,
            "timestamp": datetime.now().isoformat()
        }
        
        # Print results
        if comparison.get("comparison_possible", False):
            print(f"✅ Pipeline executed successfully")
            print(f"📊 Results:")
            print(f"   Rows: {result['actual']['rows']} (expected: {result['expected']['rows']}) - {'✅' if comparison['rows_match'] else '❌'} ({comparison['rows_score']}/50 pts)")
            print(f"   Columns Count: {result['actual']['columns_count']} (expected: {result['expected']['columns_count']}) - {'✅' if comparison['columns_count_match'] else '❌'} ({comparison['columns_count_score']}/40 pts)")
            print(f"   Column Names: {'✅' if comparison['column_names_match'] else '❌'} ({comparison['column_names_score']}/10 pts)")
            print(f"🏆 Total Score: {result['score']}/100")
        else:
            print(f"❌ Evaluation failed: {result['actual']['error']}")
            print(f"🏆 Total Score: {result['score']}/100")
        
        return result
    
    def evaluate_all_questions(self, max_questions: int = None) -> Dict[str, Any]:
        """Evaluate all questions or a subset."""
        print("🚀 SQL Agent Accuracy Evaluation")
        print("=" * 50)
        
        questions_to_test = test_questions[:max_questions] if max_questions else test_questions
        print(f"📋 Evaluating {len(questions_to_test)} questions")
        
        results = {}
        total_score = 0
        max_total_score = 0
        successful_evaluations = 0
        
        start_time = datetime.now()
        
        for i, question in enumerate(questions_to_test, 1):
            try:
                result = self.evaluate_question(i, question)
                results[f"Question{i}"] = result
                
                total_score += result["score"]
                max_total_score += result["max_score"]
                
                if result.get("comparison", {}).get("comparison_possible", False):
                    successful_evaluations += 1
                
            except Exception as e:
                print(f"💥 Error evaluating Question {i}: {str(e)}")
                results[f"Question{i}"] = {
                    "question_num": i,
                    "question": question,
                    "error": f"Evaluation failed: {str(e)}",
                    "score": 0,
                    "max_score": 100
                }
                max_total_score += 100
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Calculate summary statistics
        overall_accuracy = (total_score / max_total_score * 100) if max_total_score > 0 else 0
        
        summary = {
            "total_questions": len(questions_to_test),
            "successful_evaluations": successful_evaluations,
            "failed_evaluations": len(questions_to_test) - successful_evaluations,
            "total_score": total_score,
            "max_total_score": max_total_score,
            "overall_accuracy_percent": round(overall_accuracy, 2),
            "average_score_per_question": round(total_score / len(questions_to_test), 2) if questions_to_test else 0,
            "evaluation_start": start_time.isoformat(),
            "evaluation_end": end_time.isoformat(),
            "duration_seconds": duration.total_seconds()
        }
        
        # Print final summary
        print(f"\n📊 Final Evaluation Summary:")
        print(f"   Total Questions: {summary['total_questions']}")
        print(f"   Successful Evaluations: {summary['successful_evaluations']}")
        print(f"   Failed Evaluations: {summary['failed_evaluations']}")
        print(f"   Overall Accuracy: {summary['overall_accuracy_percent']:.2f}%")
        print(f"   Average Score per Question: {summary['average_score_per_question']:.2f}/100")
        print(f"   Total Duration: {duration}")
        
        return {
            "summary": summary,
            "results": results,
            "metadata": {
                "expected_results_file": EXPECTED_RESULTS_PATH,
                "database_path": DB_PATH,
                "evaluator_version": "1.0.0"
            }
        }
    
    def save_evaluation_results(self, results: Dict, output_path: str = None) -> str:
        """Save evaluation results to JSON file."""
        if output_path is None:
            output_dir = "tests/evaluation_results"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"sql_agent_evaluation_{timestamp}.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Evaluation results saved to: {output_path}")
        return output_path


# Test functions for pytest
class TestSQLAgentAccuracy:
    """Test class for SQL Agent accuracy evaluation."""
    
    @classmethod
    def setup_class(cls):
        """Setup test class."""
        cls.evaluator = SQLAgentEvaluator()
    
    def test_individual_questions(self):
        """Test individual questions (first 3 for quick testing)."""
        for i in range(1, 4):  # Test first 3 questions
            question = test_questions[i-1]
            result = self.evaluator.evaluate_question(i, question)
            
            # Assert that evaluation completed
            assert "score" in result
            assert "question_num" in result
            assert result["question_num"] == i
            
            # If comparison was possible, check score components
            if result.get("comparison", {}).get("comparison_possible", False):
                comparison = result["comparison"]
                
                # Score should be sum of components
                expected_total = (
                    comparison["rows_score"] + 
                    comparison["columns_count_score"] + 
                    comparison["column_names_score"]
                )
                assert result["score"] == expected_total
                
                # Individual scores should be valid
                assert 0 <= comparison["rows_score"] <= 50
                assert 0 <= comparison["columns_count_score"] <= 40
                assert 0 <= comparison["column_names_score"] <= 10
    
    def test_full_evaluation(self):
        """Test full evaluation of all questions."""
        results = self.evaluator.evaluate_all_questions(max_questions=5)  # Test first 5 for CI
        
        # Check summary structure
        assert "summary" in results
        assert "results" in results
        assert "metadata" in results
        
        summary = results["summary"]
        assert "total_questions" in summary
        assert "overall_accuracy_percent" in summary
        assert 0 <= summary["overall_accuracy_percent"] <= 100


def run_evaluation(max_questions: int = None, save_results: bool = True) -> str:
    """
    Main function to run the evaluation.
    
    Args:
        max_questions: Maximum number of questions to evaluate (None for all)
        save_results: Whether to save results to file
    
    Returns:
        Path to saved results file (if saved)
    """
    evaluator = SQLAgentEvaluator()
    results = evaluator.evaluate_all_questions(max_questions=max_questions)
    
    if save_results:
        return evaluator.save_evaluation_results(results)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate SQL Agent Accuracy')
    parser.add_argument('--max-questions', type=int, help='Maximum number of questions to evaluate')
    parser.add_argument('--no-save', action='store_true', help='Do not save results to file')
    
    args = parser.parse_args()
    
    try:
        result_path = run_evaluation(
            max_questions=args.max_questions,
            save_results=not args.no_save
        )
        
        if not args.no_save:
            print(f"\n🎉 Evaluation complete! Results saved to: {result_path}")
        
    except KeyboardInterrupt:
        print("\n🛑 Evaluation interrupted by user.")
    except Exception as e:
        print(f"\n💥 Evaluation failed: {e}")
