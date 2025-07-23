#!/usr/bin/env python3
"""
Main test runner script - run this from the project root
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

# Import and run the test runner
from tests.test_runner import run_all_tests

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
