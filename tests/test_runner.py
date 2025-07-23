"""
Test runner for all SQL crew integration tests
"""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all test modules
from tests.test_database import TestDatabaseUtilities
from tests.test_sql_crew import TestSQLCrew
from tests.test_integration import TestIntegrationWorkflow


def create_test_suite():
    """Create a comprehensive test suite"""
    suite = unittest.TestSuite()
    
    # Add database tests
    suite.addTest(unittest.makeSuite(TestDatabaseUtilities))
    
    # Add SQL crew tests
    suite.addTest(unittest.makeSuite(TestSQLCrew))
    
    # Add integration tests
    suite.addTest(unittest.makeSuite(TestIntegrationWorkflow))
    
    return suite


def run_all_tests(verbosity=2):
    """Run all tests with specified verbosity"""
    # Create test suite
    suite = create_test_suite()
    
    # Create test runner
    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
    
    print("=" * 70)
    print("RUNNING SQL CREW INTEGRATION TEST SUITE")
    print("=" * 70)
    print()
    
    # Run tests
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.splitlines()[-1] if traceback else 'Unknown failure'}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.splitlines()[-1] if traceback else 'Unknown error'}")
    
    # Return True if all tests passed
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == '__main__':
    # Set up environment
    print("Setting up test environment...")
    
    # Ensure database exists
    from utils.db_simulator import setup_sample_db
    if not os.path.exists("data/sample_db.sqlite"):
        print("Creating sample database...")
        setup_sample_db()
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
