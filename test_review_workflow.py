#!/usr/bin/env python3
"""
Test the SQL generation and review workflow
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from agents.sql_crew import sql_generator_crew, sql_reviewer_crew
from utils.db_simulator import get_structured_schema, run_query

def test_generation_and_review():
    print("🚀 Testing SQL Generation + Review Workflow")
    print("=" * 60)
    
    # Load database schema
    db_schema = get_structured_schema("data/sample_db.sqlite")
    print("📋 Database Schema:")
    print(db_schema)
    print()
    
    # Test queries that might need review/optimization
    test_queries = [
        "Show me all products with their prices",
        "What are the top 5 most expensive products?",
        "Count how many customers we have from each country",
    ]
    
    for i, user_query in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: {user_query}")
        print("-" * 50)
        
        try:
            # Step 1: Generate initial SQL
            print("🤖 Step 1: Generating initial SQL...")
            gen_output = sql_generator_crew.kickoff(inputs={
                "user_input": user_query, 
                "db_schema": db_schema
            })
            
            initial_sql = gen_output.pydantic.sqlquery
            print(f"📝 Initial SQL: {initial_sql}")
            
            # Step 2: Review the SQL with GPT-4o
            print("\n🔍 Step 2: Reviewing SQL with GPT-4o...")
            review_output = sql_reviewer_crew.kickoff(inputs={
                "sql_query": initial_sql,
                "db_schema": db_schema
            })
            
            reviewed_sql = review_output.pydantic.reviewed_sqlquery
            print(f"✅ Reviewed SQL: {reviewed_sql}")
            
            # Compare initial vs reviewed
            if initial_sql.strip() != reviewed_sql.strip():
                print("🔄 SQL was modified by the reviewer!")
            else:
                print("✓ SQL approved without changes")
            
            # Step 3: Execute the final query
            print("\n🔍 Step 3: Executing final query...")
            result = run_query(reviewed_sql)
            print("📊 Result:")
            print(result)
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print()

if __name__ == "__main__":
    test_generation_and_review()
