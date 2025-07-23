#!/usr/bin/env python3
"""
Test the complete workflow of SQL generation and execution
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from agents.sql_crew import sql_generator_crew
from utils.db_simulator import get_structured_schema, run_query

def test_complete_workflow():
    print("🚀 Testing Complete SQL Generation Workflow")
    print("=" * 50)
    
    # Load database schema
    db_schema = get_structured_schema("data/sample_db.sqlite")
    print("📋 Database Schema:")
    print(db_schema)
    print()
    
    # Test different types of queries
    test_queries = [
        "Show me all products with their prices",
        "Count total number of customers",
        "What are the top 3 most expensive products?",
    ]
    
    for i, user_query in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: {user_query}")
        print("-" * 40)
        
        try:
            # 1. Generate SQL using the crew
            print("🤖 Generating SQL...")
            gen_output = sql_generator_crew.kickoff(inputs={
                "user_input": user_query, 
                "db_schema": db_schema
            })
            
            sql_query = gen_output.pydantic.sqlquery
            print(f"📝 Generated SQL: {sql_query}")
            
            # 2. Execute the query
            print("🔍 Executing query...")
            result = run_query(sql_query)
            print("📊 Result:")
            print(result)
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print()

if __name__ == "__main__":
    test_complete_workflow()
