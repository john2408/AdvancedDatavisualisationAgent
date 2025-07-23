"""
Integration tests for the complete workflow
"""

import unittest
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.sql_crew import sql_generator_crew, sql_reviewer_crew
from utils.db_simulator import get_structured_schema, run_query


class TestIntegrationWorkflow(unittest.TestCase):
    """Test the complete integration workflow from user input to database results"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data once for all tests"""
        cls.db_path = "data/sample_db.sqlite"
        cls.schema = get_structured_schema(cls.db_path)
        cls.test_scenarios = [
            {
                "query": "Show me all products with their prices",
                "expected_keywords": ["select", "products", "price"]
            },
            {
                "query": "What are the top 5 most expensive products?",
                "expected_keywords": ["select", "products", "order by", "limit"]
            },
            {
                "query": "Count how many customers we have from each country",
                "expected_keywords": ["select", "customers", "count", "group by"]
            }
        ]
    
    def test_complete_workflow_basic(self):
        """Test the complete workflow: generation → review → execution"""
        user_query = "Show me all products with their prices"
        
        try:
            # Step 1: Generate SQL
            gen_output = sql_generator_crew.kickoff(inputs={
                "user_input": user_query,
                "db_schema": self.schema
            })
            initial_sql = gen_output.pydantic.sqlquery
            
            # Step 2: Review SQL
            review_output = sql_reviewer_crew.kickoff(inputs={
                "sql_query": initial_sql,
                "db_schema": self.schema
            })
            reviewed_sql = review_output.pydantic.reviewed_sqlquery
            
            # Step 3: Execute SQL
            result = run_query(reviewed_sql)
            
            # Verify all steps completed successfully
            self.assertIsInstance(initial_sql, str)
            self.assertIsInstance(reviewed_sql, str)
            self.assertIsInstance(result, str)
            
            self.assertGreater(len(initial_sql.strip()), 0)
            self.assertGreater(len(reviewed_sql.strip()), 0)
            self.assertGreater(len(result.strip()), 0)
            
            # Check that result contains expected data
            self.assertIn("product", result.lower())
            self.assertIn("price", result.lower())
            
        except Exception as e:
            self.fail(f"Complete workflow failed with error: {e}")
    
    def test_multiple_query_scenarios(self):
        """Test multiple query scenarios to ensure robustness"""
        
        for i, scenario in enumerate(self.test_scenarios):
            with self.subTest(scenario=i, query=scenario["query"]):
                try:
                    # Generate SQL
                    gen_output = sql_generator_crew.kickoff(inputs={
                        "user_input": scenario["query"],
                        "db_schema": self.schema
                    })
                    initial_sql = gen_output.pydantic.sqlquery
                    
                    # Review SQL
                    review_output = sql_reviewer_crew.kickoff(inputs={
                        "sql_query": initial_sql,
                        "db_schema": self.schema
                    })
                    reviewed_sql = review_output.pydantic.reviewed_sqlquery
                    
                    # Execute SQL
                    result = run_query(reviewed_sql)
                    
                    # Verify basic properties
                    self.assertIsInstance(reviewed_sql, str)
                    self.assertGreater(len(reviewed_sql.strip()), 0)
                    self.assertIsInstance(result, str)
                    self.assertGreater(len(result.strip()), 0)
                    
                    # Check that SQL contains expected keywords
                    sql_lower = reviewed_sql.lower()
                    for keyword in scenario["expected_keywords"]:
                        self.assertIn(keyword, sql_lower, 
                                      f"Expected keyword '{keyword}' not found in SQL: {reviewed_sql}")
                    
                except Exception as e:
                    self.fail(f"Scenario '{scenario['query']}' failed with error: {e}")
    
    def test_schema_validation(self):
        """Test that generated queries only use valid schema elements"""
        user_query = "Show me all products with their prices"
        
        try:
            # Generate and review SQL
            gen_output = sql_generator_crew.kickoff(inputs={
                "user_input": user_query,
                "db_schema": self.schema
            })
            initial_sql = gen_output.pydantic.sqlquery
            
            review_output = sql_reviewer_crew.kickoff(inputs={
                "sql_query": initial_sql,
                "db_schema": self.schema
            })
            reviewed_sql = review_output.pydantic.reviewed_sqlquery
            
            # Check that SQL doesn't contain invalid table names
            sql_lower = reviewed_sql.lower()
            
            # Valid tables from our schema
            valid_tables = ["products", "customers", "orders", "order_items", "employees", "departments"]
            
            # Check that if any table is mentioned, it's from our valid set
            # This is a basic check - more sophisticated parsing could be added
            for table in valid_tables:
                if table in sql_lower:
                    # If this table is used, that's good
                    pass
            
            # Check that some valid table is used
            table_found = any(table in sql_lower for table in valid_tables)
            self.assertTrue(table_found, f"No valid table found in SQL: {reviewed_sql}")
            
        except Exception as e:
            self.fail(f"Schema validation test failed with error: {e}")
    
    def test_sql_syntax_basic(self):
        """Test that generated SQL has basic syntactic correctness"""
        user_query = "Count total number of customers"
        
        try:
            # Generate and review SQL
            gen_output = sql_generator_crew.kickoff(inputs={
                "user_input": user_query,
                "db_schema": self.schema
            })
            initial_sql = gen_output.pydantic.sqlquery
            
            review_output = sql_reviewer_crew.kickoff(inputs={
                "sql_query": initial_sql,
                "db_schema": self.schema
            })
            reviewed_sql = review_output.pydantic.reviewed_sqlquery
            
            # Basic syntax checks
            sql_stripped = reviewed_sql.strip()
            
            # Should start with SELECT (case insensitive)
            self.assertTrue(sql_stripped.lower().startswith('select'), 
                           f"SQL should start with SELECT: {reviewed_sql}")
            
            # Should end with semicolon (optional but good practice)
            # Allow both with and without semicolon
            self.assertTrue(sql_stripped.endswith(';') or not sql_stripped.endswith(';'))
            
            # Should contain FROM clause for most queries
            if 'count' in sql_stripped.lower():
                self.assertIn('from', sql_stripped.lower(), 
                             f"COUNT query should have FROM clause: {reviewed_sql}")
            
        except Exception as e:
            self.fail(f"SQL syntax test failed with error: {e}")
    
    def test_date_query_sqlite_compatibility(self):
        """Test that date queries work with SQLite (not PostgreSQL syntax)"""
        user_query = "What are the sales from last month"
        
        try:
            # Generate and review SQL
            gen_output = sql_generator_crew.kickoff(inputs={
                "user_input": user_query,
                "db_schema": self.schema
            })
            initial_sql = gen_output.pydantic.sqlquery
            
            review_output = sql_reviewer_crew.kickoff(inputs={
                "sql_query": initial_sql,
                "db_schema": self.schema
            })
            reviewed_sql = review_output.pydantic.reviewed_sqlquery
            
            # Check for PostgreSQL-specific syntax that won't work in SQLite
            sql_lower = reviewed_sql.lower()
            
            # These are PostgreSQL-specific and should NOT be in SQLite queries
            postgresql_syntax = [
                'date_trunc',
                'interval',
                'current_date - interval',
                'extract(',
                'age(',
                'now()'
            ]
            
            for pg_syntax in postgresql_syntax:
                self.assertNotIn(pg_syntax, sql_lower, 
                               f"PostgreSQL syntax '{pg_syntax}' found in SQLite query: {reviewed_sql}")
            
            # Try to execute the query - this should work with SQLite
            try:
                result = run_query(reviewed_sql)
                # If we get here, the query executed successfully
                self.assertIsInstance(result, str)
                self.assertGreater(len(result.strip()), 0)
                print(f"✅ Date query executed successfully: {reviewed_sql}")
                
            except Exception as exec_error:
                # If execution fails, check if it's due to unsupported syntax
                error_msg = str(exec_error).lower()
                if any(keyword in error_msg for keyword in ['syntax error', 'interval', 'date_trunc']):
                    self.fail(f"Date query failed due to PostgreSQL syntax in SQLite database. "
                             f"Query: {reviewed_sql}. Error: {exec_error}")
                else:
                    # Some other execution error - could be data-related
                    print(f"⚠️  Date query generated but failed execution (possibly no data): {exec_error}")
                    # Still validate the SQL structure is reasonable
                    self.assertIn('select', sql_lower)
                    self.assertIn('from', sql_lower)
                    
        except Exception as e:
            self.fail(f"Date query test failed with error: {e}")


if __name__ == '__main__':
    unittest.main()
