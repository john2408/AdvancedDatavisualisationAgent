#!/usr/bin/env python3
"""
Test script to verify SQL crew integration works correctly
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from agents.sql_crew import sql_generator_crew
from utils.db_simulator import get_structured_schema

# Test the SQL generator agent
def test_sql_generation():
    print("Testing SQL Query Generation...")
    
    # Load database schema
    db_schema = get_structured_schema("data/sample_db.sqlite")
    print(f"Database Schema:\n{db_schema}\n")
    
    # Test queries
    test_queries = [
        "Show me all products and their prices",
        "What are the top 5 customers by total order amount?",
        "Show monthly sales trends for 2024"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 50)
        
        try:
            # Generate SQL using the crew
            gen_output = sql_generator_crew.kickoff(inputs={
                "user_input": query, 
                "db_schema": db_schema
            })
            
            sql_query = gen_output.pydantic.sqlquery
            print(f"Generated SQL: {sql_query}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_sql_generation()
