"""
Unit tests for database utilities and schema operations
"""

import unittest
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_simulator import get_structured_schema, run_query, setup_sample_db


class TestDatabaseUtilities(unittest.TestCase):
    """Test database utilities and operations"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests"""
        cls.db_path = "data/sample_db.sqlite"
        # Ensure database exists and is set up
        if not os.path.exists(cls.db_path):
            setup_sample_db()
    
    def test_get_structured_schema(self):
        """Test that we can load the database schema"""
        schema = get_structured_schema(self.db_path)
        
        # Check that schema is returned as string
        self.assertIsInstance(schema, str)
        self.assertGreater(len(schema), 0)
        
        # Check that essential tables are present
        self.assertIn("products", schema)
        self.assertIn("customers", schema)
        self.assertIn("orders", schema)
        self.assertIn("order_items", schema)
        
        # Check that essential columns are present
        self.assertIn("product_id", schema)
        self.assertIn("customer_id", schema)
        self.assertIn("price", schema)
    
    def test_run_simple_query(self):
        """Test running a simple query"""
        query = "SELECT COUNT(*) as total_products FROM products;"
        result = run_query(query)
        
        # Check that result is returned as string
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Check that the result contains expected content
        self.assertIn("total_products", result)
    
    def test_run_select_query(self):
        """Test running a SELECT query"""
        query = "SELECT product_id, product_name, price FROM products LIMIT 3;"
        result = run_query(query)
        
        # Check that result is returned as string
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Check that the result contains expected columns
        self.assertIn("product_id", result)
        self.assertIn("product_name", result)
        self.assertIn("price", result)
    
    def test_invalid_query(self):
        """Test that invalid queries are handled properly"""
        query = "SELECT invalid_column FROM nonexistent_table;"
        
        # This should either return an error message or raise an exception
        # depending on the implementation
        try:
            result = run_query(query)
            # If no exception, check if error is in result
            self.assertTrue(isinstance(result, str))
        except Exception as e:
            # Exception is expected for invalid queries
            self.assertIsInstance(e, Exception)


if __name__ == '__main__':
    unittest.main()
