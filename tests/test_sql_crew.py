"""
Unit tests for SQL crew agents and their functionality
"""

import unittest
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.crew_agents import sql_generator_crew, sql_reviewer_crew, sql_compliance_crew
from utils.db_simulator import get_structured_schema


class TestSQLCrew(unittest.TestCase):
    """Test SQL crew agents and their functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data once for all tests"""
        cls.db_path = "data/sample_db.sqlite"
        cls.schema = get_structured_schema(cls.db_path)
        cls.test_queries = [
            "Show me all products with their prices",
            "What are the top 5 most expensive products?",
            "Count how many customers we have from each country"
        ]
    
    def test_sql_generator_crew_import(self):
        """Test that SQL generator crew can be imported"""
        self.assertIsNotNone(sql_generator_crew)
        self.assertEqual(len(sql_generator_crew.agents), 1)
        self.assertEqual(len(sql_generator_crew.tasks), 1)
    
    def test_sql_reviewer_crew_import(self):
        """Test that SQL reviewer crew can be imported"""
        self.assertIsNotNone(sql_reviewer_crew)
        self.assertEqual(len(sql_reviewer_crew.agents), 1)
        self.assertEqual(len(sql_reviewer_crew.tasks), 1)
    
    def test_sql_compliance_crew_import(self):
        """Test that SQL compliance crew can be imported"""
        self.assertIsNotNone(sql_compliance_crew)
        self.assertEqual(len(sql_compliance_crew.agents), 1)
        self.assertEqual(len(sql_compliance_crew.tasks), 1)
    
    def test_sql_generation_basic(self):
        """Test basic SQL generation functionality"""
        user_input = "Show me all products with their prices"
        
        try:
            # Test that we can kickoff the SQL generation crew
            gen_output = sql_generator_crew.kickoff(inputs={
                "user_input": user_input,
                "db_schema": self.schema
            })
            
            # Check that we get a pydantic output
            self.assertIsNotNone(gen_output)
            self.assertTrue(hasattr(gen_output, 'pydantic'))
            self.assertTrue(hasattr(gen_output.pydantic, 'sqlquery'))
            
            # Check that the SQL query is a string
            sql_query = gen_output.pydantic.sqlquery
            self.assertIsInstance(sql_query, str)
            self.assertGreater(len(sql_query.strip()), 0)
            
            # Check that the SQL contains expected keywords
            sql_lower = sql_query.lower()
            self.assertIn('select', sql_lower)
            self.assertIn('products', sql_lower)
            
        except Exception as e:
            self.fail(f"SQL generation failed with error: {e}")
    
    def test_sql_review_basic(self):
        """Test basic SQL review functionality"""
        test_sql = "SELECT product_id, product_name, price FROM products;"
        
        try:
            # Test that we can kickoff the SQL review crew
            review_output = sql_reviewer_crew.kickoff(inputs={
                "sql_query": test_sql,
                "db_schema": self.schema
            })
            
            # Check that we get a pydantic output
            self.assertIsNotNone(review_output)
            self.assertTrue(hasattr(review_output, 'pydantic'))
            self.assertTrue(hasattr(review_output.pydantic, 'reviewed_sqlquery'))
            
            # Check that the reviewed SQL query is a string
            reviewed_sql = review_output.pydantic.reviewed_sqlquery
            self.assertIsInstance(reviewed_sql, str)
            self.assertGreater(len(reviewed_sql.strip()), 0)
            
        except Exception as e:
            self.fail(f"SQL review failed with error: {e}")
    
    def test_generation_and_review_workflow(self):
        """Test the complete generation and review workflow"""
        user_input = "What are the top 3 most expensive products?"
        
        try:
            # Step 1: Generate SQL
            gen_output = sql_generator_crew.kickoff(inputs={
                "user_input": user_input,
                "db_schema": self.schema
            })
            initial_sql = gen_output.pydantic.sqlquery
            
            # Step 2: Review SQL
            review_output = sql_reviewer_crew.kickoff(inputs={
                "sql_query": initial_sql,
                "db_schema": self.schema
            })
            reviewed_sql = review_output.pydantic.reviewed_sqlquery
            
            # Check that both steps completed successfully
            self.assertIsInstance(initial_sql, str)
            self.assertIsInstance(reviewed_sql, str)
            self.assertGreater(len(initial_sql.strip()), 0)
            self.assertGreater(len(reviewed_sql.strip()), 0)
            
            # Check that SQL contains expected elements for this query
            reviewed_lower = reviewed_sql.lower()
            self.assertIn('select', reviewed_lower)
            self.assertIn('products', reviewed_lower)
            self.assertIn('order by', reviewed_lower)
            self.assertIn('limit', reviewed_lower)
            
        except Exception as e:
            self.fail(f"Generation and review workflow failed with error: {e}")


if __name__ == '__main__':
    unittest.main()
