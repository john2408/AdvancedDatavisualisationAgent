#!/usr/bin/env python3
"""
Test to evaluate SQL agent accuracy by comparing generated results with expected results.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, asdict

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from agents.crew_agents import sql_generator_crew, sql_reviewer_crew
from backend.sql_utils import run_query
from omegaconf import OmegaConf
from tests.test_data.sample_sql_questions import test_questions
@dataclass
class SingleRunResult:
    """Represents results from a single run of a question."""
    question_num: int
    run_num: int
    question: str
    success: bool
    rows_score: int
    columns_count_score: int
    column_names_score: int
    total_score: int
    expected_rows: int
    actual_rows: int
    expected_columns_count: int
    actual_columns_count: int
    expected_columns: List[str]
    actual_columns: List[str]
    error: str = None
    timestamp: str = ""



# Load configuration
config = OmegaConf.load("config.yaml")
DB_PATH = config.db_path
db_schema_agent = config.db_schema_agent

# Load expected results
EXPECTED_RESULTS_PATH = "tests/test_data/generated/complete_test_data.json"

class SQLAgentEvaluator:
    """Evaluates SQL agent accuracy against expected results with multiple runs support."""
    
    def __init__(self):
        """Initialize the evaluator."""
        self.expected_results = self._load_expected_results()
        self.scoring_results = {}
        self.all_runs_data = []  # Store all individual run results
        
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
    
    def evaluate_single_run(self, question_num: int, run_num: int, question: str) -> SingleRunResult:
        """Evaluate a single run of a question."""
        print(f"  📋 Run {run_num}: {question[:50]}...")
        
        # Get expected results
        expected_key = f"Question{question_num}"
        if expected_key not in self.expected_results:
            return SingleRunResult(
                question_num=question_num,
                run_num=run_num,
                question=question,
                success=False,
                rows_score=0,
                columns_count_score=0,
                column_names_score=0,
                total_score=0,
                expected_rows=0,
                actual_rows=0,
                expected_columns_count=0,
                actual_columns_count=0,
                expected_columns=[],
                actual_columns=[],
                error=f"No expected results found for {expected_key}",
                timestamp=datetime.now().isoformat()
            )
        
        expected = self.expected_results[expected_key]
        
        # Execute SQL pipeline
        actual = self._execute_sql_pipeline(question)
        
        # Compare results
        comparison = self._compare_results(actual, expected)
        
        # Create run result
        run_result = SingleRunResult(
            question_num=question_num,
            run_num=run_num,
            question=question,
            success=actual["success"] and comparison.get("comparison_possible", False),
            rows_score=comparison.get("rows_score", 0),
            columns_count_score=comparison.get("columns_count_score", 0),
            column_names_score=comparison.get("column_names_score", 0),
            total_score=comparison.get("total_score", 0),
            expected_rows=expected.get("Rows", 0),
            actual_rows=actual.get("rows", 0),
            expected_columns_count=len(expected.get("Columns", [])),
            actual_columns_count=len(actual.get("columns", [])),
            expected_columns=expected.get("Columns", []),
            actual_columns=actual.get("columns", []),
            error=actual.get("error") if not actual["success"] else None,
            timestamp=datetime.now().isoformat()
        )
        
        # Store in all runs data
        self.all_runs_data.append(run_result)
        
        return run_result
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """Calculate statistical metrics for a list of values."""
        if not values:
            return {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0, "count": 0}
        
        values_array = np.array(values)
        
        return {
            "count": len(values),
            "mean": float(np.mean(values_array)),
            "median": float(np.median(values_array)),
            "std": float(np.std(values_array)),
            "min": float(np.min(values_array)),
            "max": float(np.max(values_array))
        }
    
    def evaluate_question(self, question_num: int, question: str, runs: int = 1) -> Dict[str, Any]:
        """Evaluate a single question with multiple runs."""
        print(f"\n🔄 Evaluating Question {question_num} ({runs} runs): {question}")
        print("-" * 80)
        
        run_results = []
        
        # Execute multiple runs
        for run_num in range(1, runs + 1):
            run_result = self.evaluate_single_run(question_num, run_num, question)
            run_results.append(run_result)
        
        # Calculate statistics across runs
        successful_runs = [r for r in run_results if r.success]
        
        if successful_runs:
            # Calculate stats for scoring metrics
            rows_scores = [r.rows_score for r in successful_runs]
            columns_count_scores = [r.columns_count_score for r in successful_runs]
            column_names_scores = [r.column_names_score for r in successful_runs]
            total_scores = [r.total_score for r in successful_runs]
            
            stats = {
                "rows_score": self._calculate_stats(rows_scores),
                "columns_count_score": self._calculate_stats(columns_count_scores),
                "column_names_score": self._calculate_stats(column_names_scores),
                "total_score": self._calculate_stats(total_scores)
            }
        else:
            # No successful runs
            stats = {
                "rows_score": {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0, "count": 0},
                "columns_count_score": {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0, "count": 0},
                "column_names_score": {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0, "count": 0},
                "total_score": {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0, "count": 0}
            }
        
        # Create evaluation result
        result = {
            "question_num": question_num,
            "question": question,
            "total_runs": runs,
            "successful_runs": len(successful_runs),
            "failed_runs": runs - len(successful_runs),
            "success_rate": len(successful_runs) / runs * 100 if runs > 0 else 0,
            "expected": {
                "rows": run_results[0].expected_rows if run_results else 0,
                "columns": run_results[0].expected_columns if run_results else [],
                "columns_count": run_results[0].expected_columns_count if run_results else 0
            },
            "statistics": stats,
            "individual_runs": [asdict(r) for r in run_results],
            "max_score": 100,
            "timestamp": datetime.now().isoformat()
        }
        
        # Print results summary
        print(f"✅ Completed {runs} runs - Success Rate: {result['success_rate']:.1f}%")
        if successful_runs:
            print(f"📊 Average Scores:")
            print(f"   Rows: {stats['rows_score']['mean']:.1f}/50 (std: {stats['rows_score']['std']:.1f})")
            print(f"   Columns Count: {stats['columns_count_score']['mean']:.1f}/40 (std: {stats['columns_count_score']['std']:.1f})")
            print(f"   Column Names: {stats['column_names_score']['mean']:.1f}/10 (std: {stats['column_names_score']['std']:.1f})")
            print(f"🏆 Average Total Score: {stats['total_score']['mean']:.1f}/100 (std: {stats['total_score']['std']:.1f})")
        else:
            print(f"❌ All {runs} runs failed")
        
        return result
    
    def evaluate_all_questions(self, max_questions: int = None, runs: int = 1) -> Dict[str, Any]:
        """Evaluate all questions or a subset with multiple runs."""
        print("🚀 SQL Agent Accuracy Evaluation")
        print("=" * 50)
        
        questions_to_test = test_questions[:max_questions] if max_questions else test_questions
        print(f"📋 Evaluating {len(questions_to_test)} questions with {runs} runs each")
        
        results = {}
        total_score = 0
        max_total_score = 0
        successful_evaluations = 0
        total_runs_executed = 0
        total_successful_runs = 0
        
        start_time = datetime.now()
        
        for i, question in enumerate(questions_to_test, 1):
            try:
                result = self.evaluate_question(i, question, runs)
                results[f"Question{i}"] = result
                
                # Aggregate statistics
                avg_score = result["statistics"]["total_score"]["mean"]
                total_score += avg_score
                max_total_score += result["max_score"]
                
                total_runs_executed += result["total_runs"]
                total_successful_runs += result["successful_runs"]
                
                if result["successful_runs"] > 0:
                    successful_evaluations += 1
                
            except Exception as e:
                print(f"💥 Error evaluating Question {i}: {str(e)}")
                results[f"Question{i}"] = {
                    "question_num": i,
                    "question": question,
                    "error": f"Evaluation failed: {str(e)}",
                    "total_runs": runs,
                    "successful_runs": 0,
                    "failed_runs": runs,
                    "success_rate": 0,
                    "statistics": {
                        "total_score": {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0}
                    },
                    "max_score": 100
                }
                max_total_score += 100
                total_runs_executed += runs
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Calculate summary statistics
        overall_accuracy = (total_score / max_total_score * 100) if max_total_score > 0 else 0
        overall_success_rate = (total_successful_runs / total_runs_executed * 100) if total_runs_executed > 0 else 0
        
        summary = {
            "total_questions": len(questions_to_test),
            "runs_per_question": runs,
            "total_runs_executed": total_runs_executed,
            "total_successful_runs": total_successful_runs,
            "overall_success_rate_percent": round(overall_success_rate, 2),
            "questions_with_successful_runs": successful_evaluations,
            "questions_with_zero_success": len(questions_to_test) - successful_evaluations,
            "average_score_across_questions": round(total_score / len(questions_to_test), 2) if questions_to_test else 0,
            "overall_accuracy_percent": round(overall_accuracy, 2),
            "evaluation_start": start_time.isoformat(),
            "evaluation_end": end_time.isoformat(),
            "duration_seconds": duration.total_seconds()
        }
        
        # Print final summary
        print(f"\n📊 Final Evaluation Summary:")
        print(f"   Total Questions: {summary['total_questions']}")
        print(f"   Runs per Question: {summary['runs_per_question']}")
        print(f"   Total Runs Executed: {summary['total_runs_executed']}")
        print(f"   Overall Success Rate: {summary['overall_success_rate_percent']:.2f}%")
        print(f"   Questions with Successful Runs: {summary['questions_with_successful_runs']}")
        print(f"   Average Score Across Questions: {summary['average_score_across_questions']:.2f}/100")
        print(f"   Total Duration: {duration}")
        
        return {
            "summary": summary,
            "results": results,
            "all_runs_dataframe": self.create_runs_dataframe(),
            "metadata": {
                "expected_results_file": EXPECTED_RESULTS_PATH,
                "database_path": DB_PATH,
            }
        }
    
    def create_runs_dataframe(self) -> pd.DataFrame:
        """Create a pandas DataFrame with all individual run results."""
        if not self.all_runs_data:
            return pd.DataFrame()
        
        # Convert all run results to DataFrame
        df_data = []
        for run_result in self.all_runs_data:
            df_data.append({
                'question_num': run_result.question_num,
                'run_num': run_result.run_num,
                'question': run_result.question[:100] + "..." if len(run_result.question) > 100 else run_result.question,
                'success': run_result.success,
                'rows_score': run_result.rows_score,
                'columns_count_score': run_result.columns_count_score,
                'column_names_score': run_result.column_names_score,
                'total_score': run_result.total_score,
                'expected_rows': run_result.expected_rows,
                'actual_rows': run_result.actual_rows,
                'expected_columns_count': run_result.expected_columns_count,
                'actual_columns_count': run_result.actual_columns_count,
                'error': run_result.error,
                'timestamp': run_result.timestamp
            })
        
        return pd.DataFrame(df_data)
    
    def generate_markdown_report(self, evaluation_results: Dict[str, Any], output_path: str = None) -> str:
        """Generate comprehensive markdown report with statistical analysis."""
        if output_path is None:
            output_dir = "tests/evaluation_results"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"sql_agent_robustness_evaluation_{timestamp}.md")
        
        summary = evaluation_results["summary"]
        results = evaluation_results["results"]
        df = evaluation_results["all_runs_dataframe"]
        metadata = evaluation_results["metadata"]
        
        # Generate markdown content
        markdown_content = self.create_markdown_content(summary, results, df, metadata)
        
        # Write markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Generate CSV file with all runs data
        csv_path = str(output_path).replace('.md', '_all_runs.csv')
        if not df.empty:
            df.to_csv(csv_path, index=False, encoding='utf-8')
        
        # Generate summary CSV file
        summary_csv_path = str(output_path).replace('.md', '_summary.csv')
        self.generate_summary_csv(results, summary_csv_path)
        
        print(f"📊 Markdown report generated: {output_path}")
        print(f"📄 All runs CSV generated: {csv_path}")
        print(f"📄 Summary CSV generated: {summary_csv_path}")
        return str(output_path)
    
    def generate_summary_csv(self, results: Dict, csv_path: str) -> None:
        """Generate summary CSV file with question-level statistics."""
        csv_data = []
        
        for question_key, result in results.items():
            if isinstance(result, dict) and "statistics" in result:
                stats = result["statistics"]
                csv_data.append({
                    "question_num": result.get("question_num", 0),
                    "question": result.get("question", "")[:100],
                    "total_runs": result.get("total_runs", 0),
                    "successful_runs": result.get("successful_runs", 0),
                    "success_rate_percent": result.get("success_rate", 0),
                    "rows_score_mean": stats.get("rows_score", {}).get("mean", 0),
                    "rows_score_std": stats.get("rows_score", {}).get("std", 0),
                    "columns_count_score_mean": stats.get("columns_count_score", {}).get("mean", 0),
                    "columns_count_score_std": stats.get("columns_count_score", {}).get("std", 0),
                    "column_names_score_mean": stats.get("column_names_score", {}).get("mean", 0),
                    "column_names_score_std": stats.get("column_names_score", {}).get("std", 0),
                    "total_score_mean": stats.get("total_score", {}).get("mean", 0),
                    "total_score_std": stats.get("total_score", {}).get("std", 0),
                    "expected_rows": result.get("expected", {}).get("rows", 0),
                    "expected_columns_count": result.get("expected", {}).get("columns_count", 0)
                })
        
        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_path, index=False, encoding='utf-8')
    
    def create_markdown_content(self, summary: Dict, results: Dict, df: pd.DataFrame, metadata: Dict) -> str:
        """Create the markdown content for the robustness evaluation report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# SQL Agent Robustness Evaluation Report

**Generated on:** {timestamp}  
**Evaluation Duration:** {summary['duration_seconds']:.2f} seconds  
**Questions Evaluated:** {summary['total_questions']}  
**Runs per Question:** {summary['runs_per_question']}  
**Total Runs Executed:** {summary['total_runs_executed']}  
**Total Successful Runs:** {summary['total_successful_runs']}  

## Executive Summary

This report evaluates the robustness and consistency of the SQL agent by running each question multiple times and analyzing the variance in results. The evaluation measures three key scoring components:

1. **Rows Score** (50 points): Accuracy of the number of rows returned
2. **Columns Count Score** (40 points): Correctness of the number of columns
3. **Column Names Score** (10 points): Exact match of column names

## Overall Performance Metrics

### Success Rate Analysis
- **Overall Success Rate**: {summary['overall_success_rate_percent']:.2f}%
- **Questions with at least one successful run**: {summary['questions_with_successful_runs']}/{summary['total_questions']}
- **Questions with zero successful runs**: {summary['questions_with_zero_success']}/{summary['total_questions']}
- **Average Score Across Questions**: {summary['average_score_across_questions']:.2f}/100

### Robustness Metrics

"""
        
        # Calculate global statistics if we have data
        if not df.empty:
            successful_runs = df[df['success'] == True]
            if not successful_runs.empty:
                content += self.generate_global_statistics_section(successful_runs)
            else:
                content += "No successful runs to analyze.\n\n"
        
        # Question-by-question analysis
        content += self.generate_question_analysis_section(results)
        
        # Score distribution analysis
        if not df.empty:
            content += self.generate_score_distribution_section(df)
        
        # Variance analysis
        content += self.generate_variance_analysis_section(results)
        
        # Detailed results table
        content += self.generate_detailed_results_table(results)
        
        # Technical metadata
        content += f"""## Technical Details

- **Evaluator Version**: {metadata.get('evaluator_version', 'Unknown')}
- **Expected Results File**: {metadata.get('expected_results_file', 'Unknown')}
- **Database Path**: {metadata.get('database_path', 'Unknown')}
- **Evaluation Start**: {summary['evaluation_start']}
- **Evaluation End**: {summary['evaluation_end']}

"""
        
        return content
    
    def generate_global_statistics_section(self, successful_runs: pd.DataFrame) -> str:
        """Generate global statistics section for successful runs."""
        content = "#### Global Statistics (Successful Runs Only)\n\n"
        
        # Calculate statistics for each score component
        score_columns = ['rows_score', 'columns_count_score', 'column_names_score', 'total_score']
        
        content += "| Metric | Mean | Median | Std Dev | Min | Max | Count |\n"
        content += "|--------|------|--------|---------|-----|-----|-------|\n"
        
        for col in score_columns:
            if col in successful_runs.columns:
                values = successful_runs[col]
                content += f"| **{col.replace('_', ' ').title()}** | {values.mean():.2f} | {values.median():.2f} | {values.std():.2f} | {values.min():.0f} | {values.max():.0f} | {len(values)} |\n"
        
        content += "\n"
        return content
    
    def generate_question_analysis_section(self, results: Dict) -> str:
        """Generate question-by-question analysis section."""
        content = "## Question-by-Question Analysis\n\n"
        
        # Calculate overall statistics
        high_variance_questions = []
        consistent_questions = []
        
        for question_key, result in results.items():
            if isinstance(result, dict) and "statistics" in result:
                question_num = result.get("question_num", 0)
                stats = result["statistics"]
                total_score_std = stats.get("total_score", {}).get("std", 0)
                success_rate = result.get("success_rate", 0)
                
                if total_score_std > 10:  # High variance threshold
                    high_variance_questions.append((question_num, total_score_std, success_rate))
                elif total_score_std < 5 and success_rate > 80:  # Consistent performance threshold
                    consistent_questions.append((question_num, total_score_std, success_rate))
        
        content += f"### Performance Categories\n\n"
        content += f"- **High Variance Questions** (std > 10): {len(high_variance_questions)} questions\n"
        content += f"- **Consistent Questions** (std < 5, success > 80%): {len(consistent_questions)} questions\n\n"
        
        if high_variance_questions:
            content += "#### High Variance Questions\n\n"
            content += "| Question | Std Dev | Success Rate |\n"
            content += "|----------|---------|-------------|\n"
            for q_num, std_dev, success_rate in sorted(high_variance_questions, key=lambda x: x[1], reverse=True)[:5]:
                content += f"| Q{q_num} | {std_dev:.2f} | {success_rate:.1f}% |\n"
            content += "\n"
        
        if consistent_questions:
            content += "#### Most Consistent Questions\n\n"
            content += "| Question | Std Dev | Success Rate |\n"
            content += "|----------|---------|-------------|\n"
            for q_num, std_dev, success_rate in sorted(consistent_questions, key=lambda x: x[1])[:5]:
                content += f"| Q{q_num} | {std_dev:.2f} | {success_rate:.1f}% |\n"
            content += "\n"
        
        return content
    
    def generate_score_distribution_section(self, df: pd.DataFrame) -> str:
        """Generate score distribution analysis section."""
        content = "## Score Distribution Analysis\n\n"
        
        if df.empty:
            return content + "No data available for distribution analysis.\n\n"
        
        successful_runs = df[df['success'] == True]
        
        if successful_runs.empty:
            return content + "No successful runs available for distribution analysis.\n\n"
        
        # Analyze perfect scores
        perfect_rows = len(successful_runs[successful_runs['rows_score'] == 50])
        perfect_columns_count = len(successful_runs[successful_runs['columns_count_score'] == 40])
        perfect_column_names = len(successful_runs[successful_runs['column_names_score'] == 10])
        perfect_total = len(successful_runs[successful_runs['total_score'] == 100])
        
        total_successful = len(successful_runs)
        
        content += f"### Perfect Score Analysis (out of {total_successful} successful runs)\n\n"
        content += f"- **Perfect Rows Score (50/50)**: {perfect_rows} runs ({perfect_rows/total_successful*100:.1f}%)\n"
        content += f"- **Perfect Columns Count Score (40/40)**: {perfect_columns_count} runs ({perfect_columns_count/total_successful*100:.1f}%)\n"
        content += f"- **Perfect Column Names Score (10/10)**: {perfect_column_names} runs ({perfect_column_names/total_successful*100:.1f}%)\n"
        content += f"- **Perfect Total Score (100/100)**: {perfect_total} runs ({perfect_total/total_successful*100:.1f}%)\n\n"
        
        return content
    
    def generate_variance_analysis_section(self, results: Dict) -> str:
        """Generate variance analysis section."""
        content = "## Variance Analysis\n\n"
        
        # Collect variance data
        variance_data = []
        for question_key, result in results.items():
            if isinstance(result, dict) and "statistics" in result:
                question_num = result.get("question_num", 0)
                stats = result["statistics"]
                
                variance_data.append({
                    "question": question_num,
                    "success_rate": result.get("success_rate", 0),
                    "total_score_std": stats.get("total_score", {}).get("std", 0),
                    "rows_score_std": stats.get("rows_score", {}).get("std", 0),
                    "columns_count_score_std": stats.get("columns_count_score", {}).get("std", 0),
                    "column_names_score_std": stats.get("column_names_score", {}).get("std", 0)
                })
        
        if not variance_data:
            return content + "No variance data available.\n\n"
        
        # Calculate summary statistics
        variance_df = pd.DataFrame(variance_data)
        
        content += "### Standard Deviation Summary Across All Questions\n\n"
        content += "| Score Component | Mean Std | Max Std | Questions with Std > 5 |\n"
        content += "|-----------------|----------|---------|------------------------|\n"
        
        score_cols = ['total_score_std', 'rows_score_std', 'columns_count_score_std', 'column_names_score_std']
        for col in score_cols:
            if col in variance_df.columns:
                mean_std = variance_df[col].mean()
                max_std = variance_df[col].max()
                high_variance_count = len(variance_df[variance_df[col] > 5])
                col_name = col.replace('_std', '').replace('_', ' ').title()
                content += f"| {col_name} | {mean_std:.2f} | {max_std:.2f} | {high_variance_count} |\n"
        
        content += "\n"
        return content
    
    def generate_detailed_results_table(self, results: Dict) -> str:
        """Generate detailed results table."""
        content = "## Detailed Results Summary\n\n"
        content += "| Q# | Question | Runs | Success Rate | Total Score (μ±σ) | Rows Score (μ±σ) | Cols Count (μ±σ) | Col Names (μ±σ) |\n"
        content += "|----|----------|------|--------------|-------------------|------------------|------------------|------------------|\n"
        
        for i in range(1, len(results) + 1):
            question_key = f"Question{i}"
            if question_key in results:
                result = results[question_key]
                if isinstance(result, dict) and "statistics" in result:
                    question_text = result.get("question", "")[:30] + "..." if len(result.get("question", "")) > 30 else result.get("question", "")
                    runs = result.get("total_runs", 0)
                    success_rate = result.get("success_rate", 0)
                    
                    stats = result["statistics"]
                    
                    # Format mean ± std for each score component
                    total_score = f"{stats.get('total_score', {}).get('mean', 0):.1f}±{stats.get('total_score', {}).get('std', 0):.1f}"
                    rows_score = f"{stats.get('rows_score', {}).get('mean', 0):.1f}±{stats.get('rows_score', {}).get('std', 0):.1f}"
                    cols_count_score = f"{stats.get('columns_count_score', {}).get('mean', 0):.1f}±{stats.get('columns_count_score', {}).get('std', 0):.1f}"
                    col_names_score = f"{stats.get('column_names_score', {}).get('mean', 0):.1f}±{stats.get('column_names_score', {}).get('std', 0):.1f}"
                    
                    content += f"| {i} | {question_text} | {runs} | {success_rate:.1f}% | {total_score} | {rows_score} | {cols_count_score} | {col_names_score} |\n"
        
        content += "\n"
        return content
    
    def save_evaluation_results(self, results: Dict, output_path: str = None, generate_markdown: bool = True) -> str:
        """Save evaluation results to JSON file and optionally generate markdown report."""
        if output_path is None:
            output_dir = "tests/evaluation_results"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"sql_agent_evaluation_{timestamp}.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Evaluation results saved to: {output_path}")
        
        # Generate markdown report if requested
        if generate_markdown:
            markdown_path = self.generate_markdown_report(results, output_path.replace('.json', '.md'))
            return markdown_path
        
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
            result = self.evaluator.evaluate_question(i, question, runs=2)
            
            # Assert that evaluation completed
            assert "statistics" in result
            assert "question_num" in result
            assert result["question_num"] == i
            assert result["total_runs"] == 2
            
            # If we have successful runs, check statistics structure
            if result["successful_runs"] > 0:
                stats = result["statistics"]
                
                # Check that all score components have statistics
                for score_type in ["rows_score", "columns_count_score", "column_names_score", "total_score"]:
                    assert score_type in stats
                    assert "mean" in stats[score_type]
                    assert "std" in stats[score_type]
                    assert "count" in stats[score_type]
    
    def test_full_evaluation(self):
        """Test full evaluation of all questions with multiple runs."""
        results = self.evaluator.evaluate_all_questions(max_questions=3, runs=2)  # Test first 3 for CI
        
        # Check summary structure
        assert "summary" in results
        assert "results" in results
        assert "all_runs_dataframe" in results
        assert "metadata" in results
        
        summary = results["summary"]
        assert "total_questions" in summary
        assert "runs_per_question" in summary
        assert summary["runs_per_question"] == 2
        assert "overall_success_rate_percent" in summary
        assert 0 <= summary["overall_success_rate_percent"] <= 100
        
        # Check DataFrame structure
        df = results["all_runs_dataframe"]
        if not df.empty:
            expected_columns = ['question_num', 'run_num', 'question', 'success', 'rows_score', 
                              'columns_count_score', 'column_names_score', 'total_score']
            for col in expected_columns:
                assert col in df.columns


def run_evaluation(max_questions: int = None, runs: int = 1, save_results: bool = True, generate_markdown: bool = True) -> str:
    """
    Main function to run the evaluation.
    
    Args:
        max_questions: Maximum number of questions to evaluate (None for all)
        runs: Number of times to run each question
        save_results: Whether to save results to file
        generate_markdown: Whether to generate markdown report
    
    Returns:
        Path to saved results file (if saved)
    """
    evaluator = SQLAgentEvaluator()
    results = evaluator.evaluate_all_questions(max_questions=max_questions, runs=runs)
    
    if save_results:
        return evaluator.save_evaluation_results(results, generate_markdown=generate_markdown)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate SQL Agent Accuracy with Robustness Testing')
    parser.add_argument('--max-questions', type=int, help='Maximum number of questions to evaluate')
    parser.add_argument('--runs', type=int, default=1, help='Number of times to run each question (default: 1)')
    parser.add_argument('--no-save', action='store_true', help='Do not save results to file')
    parser.add_argument('--no-markdown', action='store_true', help='Do not generate markdown report')
    
    args = parser.parse_args()
    
    try:
        print(f"🚀 Starting SQL Agent Robustness Evaluation")
        print(f"📋 Questions: {args.max_questions if args.max_questions else 'All'}")
        print(f"🔄 Runs per question: {args.runs}")
        
        result_path = run_evaluation(
            max_questions=args.max_questions,
            runs=args.runs,
            save_results=not args.no_save,
            generate_markdown=not args.no_markdown
        )
        
        if not args.no_save:
            if args.no_markdown:
                print(f"\n🎉 Evaluation complete! Results saved to: {result_path}")
            else:
                print(f"\n🎉 Evaluation complete! Report generated: {result_path}")
        
    except KeyboardInterrupt:
        print("\n🛑 Evaluation interrupted by user.")
    except Exception as e:
        print(f"\n💥 Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
