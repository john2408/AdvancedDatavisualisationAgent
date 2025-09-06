#!/usr/bin/env python3
"""
App Agent Latency Evaluation System

Evaluates the runtime performance of the 4-step agent pipeline:
1. step_1_generate_sql - SQL generation using CrewAI
2. step_2_review_sql - SQL review using CrewAI  
3. step_3_execute_query - Query execution
4. step_4_generate_visualization - Visualization generation

Generates detailed markdown reports with statistical analysis.
"""

import os
import sys
import time
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Add the project root to Python path
sys.path.append('/Users/JOHTORR/Repos/AdvancedDatavisualisationAgent')

# Import test questions
from tests.test_data.sample_sql_questions import test_questions

# Import configuration
from omegaconf import OmegaConf

# Load configuration - but we'll need to mock streamlit for the app functions
config = OmegaConf.load("config.yaml")
DB_PATH = config.db_path
db_schema_agent = config.db_schema_agent

@dataclass
class StepTiming:
    """Represents timing data for a single step execution."""
    step_name: str
    question_num: int
    question: str
    start_time: float
    end_time: float
    duration_seconds: float
    success: bool
    error_message: Optional[str] = None
    additional_metadata: Optional[Dict] = None

@dataclass
class PipelineRun:
    """Represents a complete pipeline run for one question."""
    question_num: int
    question: str
    total_duration: float
    step_timings: List[StepTiming]
    success: bool
    failed_step: Optional[str] = None
    timestamp: str = ""

class MockStreamlit:
    """Mock Streamlit functions to avoid dependencies during testing."""
    
    @staticmethod
    def info(msg): print(f"ℹ️  {msg}")
    
    @staticmethod
    def success(msg): print(f"✅ {msg}")
    
    @staticmethod
    def error(msg): print(f"❌ {msg}")
    
    @staticmethod
    def warning(msg): print(f"⚠️  {msg}")

class AppLatencyEvaluator:
    """Evaluates latency performance of the app's agent pipeline."""
    
    def __init__(self):
        """Initialize the evaluator."""
        self.results: List[PipelineRun] = []
        self.setup_mock_environment()
        
    def setup_mock_environment(self):
        """Setup mock environment to run app functions without Streamlit."""
        # Mock streamlit to avoid import errors
        sys.modules['streamlit'] = MockStreamlit()
        
        # Import app functions after mocking streamlit
        try:
            # We'll need to import the functions while handling the streamlit dependency
            self.import_app_functions()
        except Exception as e:
            print(f"Warning: Could not import app functions directly: {e}")
            print("Will use alternative approach...")
    
    def import_app_functions(self):
        """Import the step functions from app.py"""
        # This is tricky because app.py imports streamlit
        # We'll implement the functions directly here with the same logic
        pass
    
    def step_1_generate_sql_standalone(self, user_query: str) -> Dict[str, Any]:
        """Standalone version of step_1_generate_sql without Streamlit dependencies."""
        try:
            from agents.crew_agents import sql_generator_crew
            
            gen_output = sql_generator_crew.kickoff(inputs={
                "user_input": user_query, 
                "db_schema": db_schema_agent
            })
            initial_sql = gen_output.pydantic.sqlquery
            
            return {
                "success": True,
                "initial_sql": initial_sql,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "initial_sql": None,
                "error": str(e)
            }
    
    def step_2_review_sql_standalone(self, initial_sql: str) -> Dict[str, Any]:
        """Standalone version of step_2_review_sql without Streamlit dependencies."""
        try:
            from agents.crew_agents import sql_reviewer_crew
            
            review_output = sql_reviewer_crew.kickoff(inputs={
                "sql_query": initial_sql, 
                "db_schema": db_schema_agent
            })
            reviewed_sql = review_output.pydantic.reviewed_sqlquery
            
            return {
                "success": True,
                "reviewed_sql": reviewed_sql,
                "was_changed": initial_sql.strip() != reviewed_sql.strip(),
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "reviewed_sql": initial_sql,  # Fallback to original
                "was_changed": False,
                "error": str(e)
            }
    
    def step_3_execute_query_standalone(self, reviewed_sql: str) -> Dict[str, Any]:
        """Standalone version of step_3_execute_query without Streamlit dependencies."""
        try:
            from backend.sql_utils import run_query
            
            query_result = run_query(reviewed_sql, DB_PATH)
            
            if query_result is not None and isinstance(query_result, pd.DataFrame) and not query_result.empty:
                if "Error" not in query_result.columns:
                    return {
                        "success": True,
                        "query_result": query_result,
                        "rows": len(query_result),
                        "columns": len(query_result.columns),
                        "error": None
                    }
                else:
                    error_msg = query_result["Error"].iloc[0]
                    return {
                        "success": False,
                        "query_result": None,
                        "error": error_msg
                    }
            else:
                return {
                    "success": False,
                    "query_result": None,
                    "error": "No data returned"
                }
        except Exception as e:
            return {
                "success": False,
                "query_result": None,
                "error": str(e)
            }
    
    def step_4_generate_visualization_standalone(self, query_result: pd.DataFrame, user_query: str) -> Dict[str, Any]:
        """Standalone version of step_4_generate_visualization without Streamlit dependencies."""
        try:
            from frontend.hybrid_visualization import step_4_hybrid_visualization
            
            # This function should work without streamlit if we mock it properly
            result = step_4_hybrid_visualization(query_result, user_query)
            
            return {
                "success": result.get("success", False),
                "figure": result.get("figure"),
                "summary": result.get("summary", ""),
                "error": result.get("error")
            }
        except Exception as e:
            return {
                "success": False,
                "figure": None,
                "summary": "Visualization generation failed",
                "error": str(e)
            }
    
    def time_step_execution(self, step_func, step_name: str, question_num: int, question: str, *args, **kwargs) -> StepTiming:
        """Time the execution of a single step."""
        start_time = time.time()
        
        try:
            result = step_func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.get("success", False) if isinstance(result, dict) else False
            error_msg = result.get("error") if isinstance(result, dict) else None
            
            return StepTiming(
                step_name=step_name,
                question_num=question_num,
                question=question,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=success,
                error_message=error_msg,
                additional_metadata=result if isinstance(result, dict) else {}
            )
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            return StepTiming(
                step_name=step_name,
                question_num=question_num,
                question=question,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=False,
                error_message=str(e)
            )
    
    def evaluate_pipeline_for_question(self, question_num: int, question: str) -> PipelineRun:
        """Evaluate the complete 4-step pipeline for a single question."""
        print(f"\n🔄 Evaluating Question {question_num}: {question}")
        print("-" * 80)
        
        step_timings = []
        pipeline_start = time.time()
        current_success = True
        failed_step = None
        
        # Step 1: Generate SQL
        step1_timing = self.time_step_execution(
            self.step_1_generate_sql_standalone, 
            "step_1_generate_sql", 
            question_num, 
            question, 
            question
        )
        step_timings.append(step1_timing)
        
        if not step1_timing.success:
            current_success = False
            failed_step = "step_1_generate_sql"
            print(f"❌ Step 1 failed: {step1_timing.error_message}")
        else:
            print(f"✅ Step 1 completed in {step1_timing.duration_seconds:.2f}s")
            
            # Step 2: Review SQL
            initial_sql = step1_timing.additional_metadata.get("initial_sql")
            if initial_sql:
                step2_timing = self.time_step_execution(
                    self.step_2_review_sql_standalone,
                    "step_2_review_sql",
                    question_num,
                    question,
                    initial_sql
                )
                step_timings.append(step2_timing)
                
                if not step2_timing.success:
                    current_success = False
                    failed_step = "step_2_review_sql"
                    print(f"❌ Step 2 failed: {step2_timing.error_message}")
                else:
                    print(f"✅ Step 2 completed in {step2_timing.duration_seconds:.2f}s")
                    
                    # Step 3: Execute Query
                    reviewed_sql = step2_timing.additional_metadata.get("reviewed_sql")
                    if reviewed_sql:
                        step3_timing = self.time_step_execution(
                            self.step_3_execute_query_standalone,
                            "step_3_execute_query",
                            question_num,
                            question,
                            reviewed_sql
                        )
                        step_timings.append(step3_timing)
                        
                        if not step3_timing.success:
                            current_success = False
                            failed_step = "step_3_execute_query"
                            print(f"❌ Step 3 failed: {step3_timing.error_message}")
                        else:
                            print(f"✅ Step 3 completed in {step3_timing.duration_seconds:.2f}s")
                            
                            # Step 4: Generate Visualization
                            query_result = step3_timing.additional_metadata.get("query_result")
                            if query_result is not None:
                                step4_timing = self.time_step_execution(
                                    self.step_4_generate_visualization_standalone,
                                    "step_4_generate_visualization",
                                    question_num,
                                    question,
                                    query_result,
                                    question
                                )
                                step_timings.append(step4_timing)
                                
                                if not step4_timing.success:
                                    # Visualization failure is not considered pipeline failure
                                    print(f"⚠️  Step 4 failed: {step4_timing.error_message}")
                                else:
                                    print(f"✅ Step 4 completed in {step4_timing.duration_seconds:.2f}s")
        
        pipeline_end = time.time()
        total_duration = pipeline_end - pipeline_start
        
        run_result = PipelineRun(
            question_num=question_num,
            question=question,
            total_duration=total_duration,
            step_timings=step_timings,
            success=current_success,
            failed_step=failed_step,
            timestamp=datetime.now().isoformat()
        )
        
        print(f"🏁 Pipeline completed in {total_duration:.2f}s ({'✅ SUCCESS' if current_success else '❌ FAILED'})")
        
        return run_result
    
    def evaluate_all_questions(self, max_questions: int = None) -> Dict[str, Any]:
        """Evaluate latency for all questions."""
        print("🚀 App Agent Latency Evaluation")
        print("=" * 50)
        
        questions_to_test = test_questions[:max_questions] if max_questions else test_questions
        print(f"📋 Evaluating {len(questions_to_test)} questions")
        
        self.results = []
        start_time = datetime.now()
        
        for i, question in enumerate(questions_to_test, 1):
            try:
                run_result = self.evaluate_pipeline_for_question(i, question)
                self.results.append(run_result)
                
                # Small delay between questions
                time.sleep(1)
                
            except KeyboardInterrupt:
                print(f"\n🛑 Evaluation interrupted. Processed {len(self.results)} questions.")
                break
            except Exception as e:
                print(f"💥 Error evaluating Question {i}: {e}")
                # Create a failed run record
                failed_run = PipelineRun(
                    question_num=i,
                    question=question,
                    total_duration=0,
                    step_timings=[],
                    success=False,
                    failed_step="evaluation_error",
                    timestamp=datetime.now().isoformat()
                )
                self.results.append(failed_run)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Calculate summary statistics
        summary = self.calculate_summary_statistics()
        
        evaluation_metadata = {
            "evaluation_start": start_time.isoformat(),
            "evaluation_end": end_time.isoformat(),
            "total_duration_seconds": duration.total_seconds(),
            "questions_evaluated": len(self.results),
            "successful_pipelines": sum(1 for r in self.results if r.success),
            "failed_pipelines": sum(1 for r in self.results if not r.success)
        }
        
        return {
            "summary": summary,
            "results": self.results,
            "metadata": evaluation_metadata
        }
    
    def calculate_summary_statistics(self) -> Dict[str, Any]:
        """Calculate detailed statistics for all steps."""
        step_names = ["step_1_generate_sql", "step_2_review_sql", "step_3_execute_query", "step_4_generate_visualization"]
        
        statistics = {
            "total_pipeline": self.calculate_step_stats([r.total_duration for r in self.results if r.success]),
            "steps": {}
        }
        
        for step_name in step_names:
            step_durations = []
            for run in self.results:
                for timing in run.step_timings:
                    if timing.step_name == step_name and timing.success:
                        step_durations.append(timing.duration_seconds)
            
            statistics["steps"][step_name] = self.calculate_step_stats(step_durations)
        
        return statistics
    
    def calculate_step_stats(self, durations: List[float]) -> Dict[str, float]:
        """Calculate statistical metrics for a list of durations."""
        if not durations:
            return {
                "count": 0,
                "mean": 0,
                "median": 0,
                "std": 0,
                "min": 0,
                "max": 0,
                "p25": 0,
                "p75": 0,
                "p95": 0,
                "p99": 0
            }
        
        durations_array = np.array(durations)
        
        return {
            "count": len(durations),
            "mean": float(np.mean(durations_array)),
            "median": float(np.median(durations_array)),
            "std": float(np.std(durations_array)),
            "min": float(np.min(durations_array)),
            "max": float(np.max(durations_array)),
            "p25": float(np.percentile(durations_array, 25)),
            "p75": float(np.percentile(durations_array, 75)),
            "p95": float(np.percentile(durations_array, 95)),
            "p99": float(np.percentile(durations_array, 99))
        }
    
    def generate_markdown_report(self, evaluation_results: Dict[str, Any], output_path: str = None) -> str:
        """Generate detailed markdown report and CSV file."""
        if output_path is None:
            output_dir = Path("tests/evaluation_results")
            output_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"app_agents_latency_evaluation_{timestamp}.md"
        
        summary = evaluation_results["summary"]
        metadata = evaluation_results["metadata"]
        results = evaluation_results["results"]
        
        # Generate markdown content
        markdown_content = self.create_markdown_content(summary, metadata, results)
        
        # Write markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Generate CSV file
        csv_path = str(output_path).replace('.md', '.csv')
        self.generate_csv_report(results, csv_path)
        
        print(f"📊 Markdown report generated: {output_path}")
        print(f"📄 CSV report generated: {csv_path}")
        return str(output_path)
    
    def generate_csv_report(self, results: List[PipelineRun], csv_path: str) -> None:
        """Generate CSV file with detailed results table."""
        csv_data = []
        
        for result in results:
            # Extract step durations
            step_durations = {timing.step_name: timing.duration_seconds 
                            for timing in result.step_timings if timing.success}
            
            # Status string
            status = "Success" if result.success else f"Failed at {result.failed_step}"
            
            csv_row = {
                "Question_Number": result.question_num,
                "Question": result.question,
                "Total_Duration_Seconds": round(result.total_duration, 2),
                "Step1_Generate_SQL_Seconds": round(step_durations.get('step_1_generate_sql', 0), 2),
                "Step2_Review_SQL_Seconds": round(step_durations.get('step_2_review_sql', 0), 2),
                "Step3_Execute_Query_Seconds": round(step_durations.get('step_3_execute_query', 0), 2),
                "Step4_Generate_Visualization_Seconds": round(step_durations.get('step_4_generate_visualization', 0), 2),
                "Status": status,
                "Failed_Step": result.failed_step if not result.success else "",
                "Timestamp": result.timestamp
            }
            csv_data.append(csv_row)
        
        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_path, index=False, encoding='utf-8')
    
    def create_markdown_content(self, summary: Dict, metadata: Dict, results: List[PipelineRun]) -> str:
        """Create the markdown content for the report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# App Agent Latency Evaluation Report

**Generated on:** {timestamp}  
**Evaluation Duration:** {metadata['total_duration_seconds']:.2f} seconds  
**Questions Evaluated:** {metadata['questions_evaluated']}  
**Successful Pipelines:** {metadata['successful_pipelines']}  
**Failed Pipelines:** {metadata['failed_pipelines']}  

## Executive Summary

This report evaluates the latency performance of the 4-step agent pipeline:

1. **Step 1**: SQL Generation using CrewAI
2. **Step 2**: SQL Review using CrewAI
3. **Step 3**: Query Execution 
4. **Step 4**: Visualization Generation

## Overall Pipeline Performance

### Total Pipeline Duration (End-to-End)
{self.format_stats_table(summary['total_pipeline'])}

## Step-by-Step Performance Analysis

"""
        
        step_names = {
            "step_1_generate_sql": "Step 1: SQL Generation",
            "step_2_review_sql": "Step 2: SQL Review", 
            "step_3_execute_query": "Step 3: Query Execution",
            "step_4_generate_visualization": "Step 4: Visualization Generation"
        }
        
        for step_key, step_title in step_names.items():
            step_stats = summary['steps'].get(step_key, {})
            content += f"### {step_title}\n\n"
            content += self.format_stats_table(step_stats)
            content += "\n"
        
        # Performance insights
        content += self.generate_performance_insights(summary, results)
        
        # Detailed results table
        content += self.generate_detailed_results_table(results)
        
        # Failure analysis
        content += self.generate_failure_analysis(results)
        
        return content
    
    def format_stats_table(self, stats: Dict[str, float]) -> str:
        """Format statistics as a markdown table."""
        if stats.get('count', 0) == 0:
            return "_No successful executions recorded_\n\n"
        
        return f"""| Metric | Value |
|--------|-------|
| **Count** | {stats['count']} |
| **Mean** | {stats['mean']:.3f}s |
| **Median** | {stats['median']:.3f}s |
| **Std Dev** | {stats['std']:.3f}s |
| **Min** | {stats['min']:.3f}s |
| **Max** | {stats['max']:.3f}s |
| **P25** | {stats['p25']:.3f}s |
| **P75** | {stats['p75']:.3f}s |
| **P95** | {stats['p95']:.3f}s |
| **P99** | {stats['p99']:.3f}s |

"""
    
    def generate_performance_insights(self, summary: Dict, results: List[PipelineRun]) -> str:
        """Generate performance insights section."""
        content = "## Performance Insights\n\n"
        
        # Find the slowest and fastest steps
        step_means = {}
        for step_name, stats in summary['steps'].items():
            if stats.get('count', 0) > 0:
                step_means[step_name] = stats['mean']
        
        if step_means:
            slowest_step = max(step_means.items(), key=lambda x: x[1])
            fastest_step = min(step_means.items(), key=lambda x: x[1])
            
            content += f"### Key Findings\n\n"
            content += f"- **Slowest Step**: {slowest_step[0]} (avg: {slowest_step[1]:.3f}s)\n"
            content += f"- **Fastest Step**: {fastest_step[0]} (avg: {fastest_step[1]:.3f}s)\n"
            
            total_mean = summary['total_pipeline'].get('mean', 0)
            if total_mean > 0:
                content += f"- **Pipeline Efficiency**: {(sum(step_means.values()) / total_mean * 100):.1f}% of time spent in measured steps\n"
        
        # Success rate analysis
        successful_runs = sum(1 for r in results if r.success)
        total_runs = len(results)
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        
        content += f"- **Success Rate**: {success_rate:.1f}% ({successful_runs}/{total_runs})\n"
        
        content += "\n"
        return content
    
    def generate_detailed_results_table(self, results: List[PipelineRun]) -> str:
        """Generate detailed results table."""
        content = "## Detailed Results\n\n"
        content += "| Q# | Question | Total Duration | Step1 | Step2 | Step3 | Step4 | Status |\n"
        content += "|----|----------|----------------|-------|-------|-------|-------|---------|\n"
        
        for result in results[:10]:  # Show first 10 for brevity
            step_durations = {timing.step_name: f"{timing.duration_seconds:.2f}s" 
                            for timing in result.step_timings if timing.success}
            
            status = "✅ Success" if result.success else f"❌ Failed at {result.failed_step}"
            question_short = result.question[:50] + "..." if len(result.question) > 50 else result.question
            
            content += f"| {result.question_num} | {question_short} | {result.total_duration:.2f}s |"
            content += f" {step_durations.get('step_1_generate_sql', 'N/A')} |"
            content += f" {step_durations.get('step_2_review_sql', 'N/A')} |"
            content += f" {step_durations.get('step_3_execute_query', 'N/A')} |"
            content += f" {step_durations.get('step_4_generate_visualization', 'N/A')} |"
            content += f" {status} |\n"
        
        if len(results) > 10:
            content += f"\n_... and {len(results) - 10} more results_\n"
        
        content += "\n"
        return content
    
    def generate_failure_analysis(self, results: List[PipelineRun]) -> str:
        """Generate failure analysis section."""
        failed_results = [r for r in results if not r.success]
        
        if not failed_results:
            return "## Failure Analysis\n\n✅ No pipeline failures detected!\n\n"
        
        content = "## Failure Analysis\n\n"
        
        # Count failures by step
        failure_counts = {}
        for result in failed_results:
            step = result.failed_step or "unknown"
            failure_counts[step] = failure_counts.get(step, 0) + 1
        
        content += "### Failures by Step\n\n"
        for step, count in sorted(failure_counts.items()):
            content += f"- **{step}**: {count} failures\n"
        
        content += "\n### Failed Questions\n\n"
        for result in failed_results:
            content += f"- **Q{result.question_num}**: {result.question[:100]}...\n"
            content += f"  - Failed at: {result.failed_step}\n"
            if result.step_timings:
                last_error = next((t.error_message for t in reversed(result.step_timings) 
                                 if t.error_message), "Unknown error")
                content += f"  - Error: {last_error}\n"
            content += "\n"
        
        return content


def main():
    """Main function for command line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate App Agent Latency')
    parser.add_argument('--max-questions', type=int, help='Maximum number of questions to evaluate')
    parser.add_argument('--output-file', type=str, help='Output markdown file path')
    parser.add_argument('--save-json', action='store_true', help='Also save raw results as JSON')
    
    args = parser.parse_args()
    
    try:
        evaluator = AppLatencyEvaluator()
        
        print(f"🚀 Starting latency evaluation...")
        if args.max_questions:
            print(f"📋 Limiting to {args.max_questions} questions")
        
        # Run evaluation
        results = evaluator.evaluate_all_questions(max_questions=args.max_questions)
        
        # Generate markdown report
        report_path = evaluator.generate_markdown_report(results, args.output_file)
        
        # Save JSON if requested
        if args.save_json:
            json_path = report_path.replace('.md', '.json')
            with open(json_path, 'w') as f:
                # Convert results to JSON-serializable format
                json_results = {
                    "summary": results["summary"],
                    "metadata": results["metadata"],
                    "results": [asdict(r) for r in results["results"]]
                }
                json.dump(json_results, f, indent=2, default=str)
            print(f"📊 JSON data saved to: {json_path}")
        
        print(f"\n🎉 Evaluation complete!")
        print(f"📊 Report: {report_path}")
        
        # Print summary
        metadata = results["metadata"]
        print(f"\n📈 Summary:")
        print(f"  Total Questions: {metadata['questions_evaluated']}")
        print(f"  Successful: {metadata['successful_pipelines']}")
        print(f"  Failed: {metadata['failed_pipelines']}")
        print(f"  Duration: {metadata['total_duration_seconds']:.2f}s")
        
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
