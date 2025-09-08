#!/usr/bin/env python3
"""
Complete test data generator - processes all 24 questions with error handling.
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from agents.crew_agents import sql_generator_crew, sql_reviewer_crew
from backend.sql_utils import run_query
from omegaconf import OmegaConf
from tests.test_data.sample_sql_questions import test_questions

# Load configuration
config = OmegaConf.load("config.yaml")
DB_PATH = config.db_path
db_schema_agent = config.db_schema_agent

def generate_sql_and_execute(question: str, question_num: int, max_retries: int = 2) -> dict:
    """Generate SQL for a question and execute it with retry logic."""
    print(f"\n🔄 Question {question_num}/24: {question}")
    print("-" * 80)
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                print(f"🔄 Retry attempt {attempt}...")
                time.sleep(2)  # Brief pause between retries
            
            # Step 1: Generate SQL
            print("📝 Generating SQL...")
            gen_output = sql_generator_crew.kickoff(inputs={
                "user_input": question, 
                "db_schema": db_schema_agent
            })
            initial_sql = gen_output.pydantic.sqlquery
            print(f"✅ Generated SQL")
            
            # Step 2: Review SQL
            print("🔍 Reviewing SQL...")
            review_output = sql_reviewer_crew.kickoff(inputs={
                "sql_query": initial_sql, 
                "db_schema": db_schema_agent
            })
            final_sql = review_output.pydantic.reviewed_sqlquery
            print(f"✅ Final SQL ready")
            
            # Step 3: Execute query
            print("⚡ Executing query...")
            query_result = run_query(final_sql, DB_PATH)
            
            if query_result is not None and isinstance(query_result, pd.DataFrame) and not query_result.empty:
                if "Error" not in query_result.columns:
                    print(f"✅ Success! Got {len(query_result)} rows, {len(query_result.columns)} columns")
                    
                    # Convert to JSON format
                    dataframe_json = query_result.to_dict('records')
                    
                    return {
                        "Question": question,
                        "SQL_Query": final_sql,
                        "Dataframe": dataframe_json,
                        "Rows": len(query_result),
                        "Columns": list(query_result.columns),
                        "Generated_At": datetime.now().isoformat(),
                        "Success": True,
                        "Attempts": attempt + 1
                    }
                else:
                    error_msg = query_result["Error"].iloc[0]
                    print(f"❌ Query error: {error_msg}")
                    if attempt == max_retries:
                        return {
                            "Question": question,
                            "SQL_Query": final_sql,
                            "Dataframe": None,
                            "Error": f"Query execution failed: {error_msg}",
                            "Success": False,
                            "Attempts": attempt + 1
                        }
            else:
                print("⚠️ No data returned")
                if attempt == max_retries:
                    return {
                        "Question": question,
                        "SQL_Query": final_sql,
                        "Dataframe": None,
                        "Error": "No data returned",
                        "Success": False,
                        "Attempts": attempt + 1
                    }
                    
        except KeyboardInterrupt:
            print("\n🛑 Process interrupted by user")
            return {
                "Question": question,
                "SQL_Query": None,
                "Dataframe": None,
                "Error": "Process interrupted by user",
                "Success": False,
                "Attempts": attempt + 1
            }
        except Exception as e:
            print(f"💥 Error: {str(e)}")
            if attempt == max_retries:
                return {
                    "Question": question,
                    "SQL_Query": None,
                    "Dataframe": None,
                    "Error": f"Processing failed: {str(e)}",
                    "Success": False,
                    "Attempts": attempt + 1
                }
            else:
                print(f"⏱️ Will retry in a moment...")
                
    # Fallback (shouldn't reach here)
    return {
        "Question": question,
        "SQL_Query": None,
        "Dataframe": None,
        "Error": "Max retries exceeded",
        "Success": False,
        "Attempts": max_retries + 1
    }

def save_progress(results: dict, output_path: str) -> None:
    """Save current progress to file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def main():
    """Main function."""
    print("🚀 Complete Test Data Generator")
    print("=" * 50)
    print(f"📋 Processing {len(test_questions)} questions")
    
    # Setup output directory
    output_dir = "tests/test_data/generated"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "complete_test_data.json")
    
    results = {}
    successful = 0
    
    start_time = datetime.now()
    
    for i, question in enumerate(test_questions, 1):
        try:
            result = generate_sql_and_execute(question, i)
            results[f"Question{i}"] = result
            
            if result["Success"]:
                successful += 1
                print(f"✅ Question {i} completed successfully")
            else:
                print(f"❌ Question {i} failed: {result['Error']}")
            
            # Save progress after each question
            save_progress(results, output_path)
            print(f"💾 Progress saved ({i}/{len(test_questions)} complete)")
            
            # Small delay between questions to avoid overwhelming the API
            if i < len(test_questions):
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Process interrupted. Saving progress...")
            save_progress(results, output_path)
            break
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Final summary
    print(f"\n📊 Final Summary:")
    print(f"   ✅ Successful: {successful}/{len(results)}")
    print(f"   ❌ Failed: {len(results) - successful}/{len(results)}")
    print(f"   ⏱️ Duration: {duration}")
    print(f"   💾 Results saved to: {output_path}")
    
    # Add metadata to results
    results["_metadata"] = {
        "total_questions": len(test_questions),
        "processed_questions": len(results) - 1,  # Exclude metadata
        "successful_questions": successful,
        "failed_questions": len(results) - 1 - successful,
        "generation_start": start_time.isoformat(),
        "generation_end": end_time.isoformat(),
        "duration_seconds": duration.total_seconds(),
        "generator_version": "1.0.0"
    }
    
    # Final save with metadata
    save_progress(results, output_path)
    
    return output_path

if __name__ == "__main__":
    try:
        output_file = main()
        print(f"\n🎉 Test data generation complete! Output: {output_file}")
    except KeyboardInterrupt:
        print("\n🛑 Generation interrupted by user.")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
    