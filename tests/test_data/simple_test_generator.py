#!/usr/bin/env python3
"""
Simple test data generator - processes just a few questions for testing.
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime

# Add the project root to Python path
sys.path.append('/Users/JOHTORR/Repos/AdvancedDatavisualisationAgent')

from agents.crew_agents import sql_generator_crew, sql_reviewer_crew
from backend.sql_utils import run_query
from omegaconf import OmegaConf

# Load configuration
config = OmegaConf.load("config.yaml")
DB_PATH = config.db_path
db_schema_agent = config.db_schema_agent

# Just test with 3 questions
test_questions = [        
        "Which fuel type showed the highest growth rate from 2023 to 2024?",
        "What is the growth rate among body types from 2023 to 2024?",
]

def generate_sql_and_execute(question: str) -> dict:
    """Generate SQL for a question and execute it."""
    print(f"\n🔄 Processing: {question}")
    print("-" * 80)
    
    try:
        # Step 1: Generate SQL
        print("📝 Generating SQL...")
        gen_output = sql_generator_crew.kickoff(inputs={
            "user_input": question, 
            "db_schema": db_schema_agent
        })
        initial_sql = gen_output.pydantic.sqlquery
        print(f"✅ Generated SQL: {initial_sql[:100]}...")
        
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
                    "Success": True
                }
            else:
                error_msg = query_result["Error"].iloc[0]
                print(f"❌ Query error: {error_msg}")
                return {
                    "Question": question,
                    "SQL_Query": final_sql,
                    "Dataframe": None,
                    "Error": f"Query execution failed: {error_msg}",
                    "Success": False
                }
        else:
            print("⚠️ No data returned")
            return {
                "Question": question,
                "SQL_Query": final_sql,
                "Dataframe": None,
                "Error": "No data returned",
                "Success": False
            }
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return {
            "Question": question,
            "SQL_Query": None,
            "Dataframe": None,
            "Error": f"Processing failed: {str(e)}",
            "Success": False
        }

def main():
    """Main function."""
    print("🚀 Simple Test Data Generator")
    print("=" * 50)
    
    results = {}
    
    for i, question in enumerate(test_questions, 1):
        result = generate_sql_and_execute(question)
        results[f"Question{i}"] = result
        
        if result["Success"]:
            print(f"✅ Question {i} completed successfully")
        else:
            print(f"❌ Question {i} failed: {result['Error']}")
    
    # Save results
    output_dir = "tests/test_data/generated"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "simple_test_data.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_path}")
    
    # Print summary
    successful = sum(1 for r in results.values() if r["Success"])
    total = len(results)
    print(f"📊 Summary: {successful}/{total} questions processed successfully")
    
    return output_path

if __name__ == "__main__":
    main()
