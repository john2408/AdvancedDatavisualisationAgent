#!/usr/bin/env python3
"""
Simple test runner for FastAPI endpoints
Tests all endpoints without requiring pytest installation
"""

import sys
import os
import json
import traceback
from typing import Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after path setup
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def assert_equal(self, actual, expected, message=""):
        if actual != expected:
            raise AssertionError(f"{message}: Expected {expected}, got {actual}")
    
    def assert_true(self, condition, message=""):
        if not condition:
            raise AssertionError(f"{message}: Expected True, got {condition}")
    
    def assert_in(self, item, container, message=""):
        if item not in container:
            raise AssertionError(f"{message}: {item} not found in {container}")
    
    def run_test(self, test_func):
        """Run a single test function"""
        test_name = test_func.__name__
        try:
            test_func()
            print(f"✅ {test_name}")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ {test_name}: {str(e)}")
            self.failed += 1
            return False
    
    def run_all_tests(self):
        """Run all test methods"""
        print("🧪 Running FastAPI Endpoint Tests")
        print("=" * 60)
        
        # Basic endpoint tests
        self.run_test(self.test_root_endpoint)
        self.run_test(self.test_health_check)
        self.run_test(self.test_config_schema)
        self.run_test(self.test_agents_list)
        
        # SQL endpoint tests
        self.run_test(self.test_sql_generator)
        self.run_test(self.test_sql_reviewer)
        self.run_test(self.test_sql_executor_missing_db)
        
        # Analysis endpoint tests
        self.run_test(self.test_data_analysis)
        self.run_test(self.test_data_visualization)
        
        # Interaction endpoint tests
        self.run_test(self.test_orchestration)
        self.run_test(self.test_data_question)
        self.run_test(self.test_alternative_visualization)
        self.run_test(self.test_follow_up_questions)
        
        # Error handling tests
        self.run_test(self.test_missing_field_validation)
        self.run_test(self.test_orchestration_missing_input)
        
        print("=" * 60)
        print(f"📊 Test Results: {self.passed} passed, {self.failed} failed")
        
        if self.failed == 0:
            print("🎉 All tests passed!")
            return True
        else:
            print("💥 Some tests failed!")
            return False

    # Basic endpoint tests
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        self.assert_equal(response.status_code, 200)
        data = response.json()
        self.assert_in("message", data)
        self.assert_equal(data["status"], "active")
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        self.assert_equal(response.status_code, 200)
        data = response.json()
        self.assert_equal(data["status"], "healthy")
        self.assert_in("message", data)
    
    def test_config_schema(self):
        """Test config schema endpoint"""
        response = client.get("/config/schema")
        self.assert_equal(response.status_code, 200)
        data = response.json()
        self.assert_in("db_schema_agent", data)
        self.assert_in("db_schema_user", data)
        self.assert_in("db_path", data)
    
    def test_agents_list(self):
        """Test agents list endpoint"""
        response = client.get("/agents/list")
        self.assert_equal(response.status_code, 200)
        data = response.json()
        self.assert_in("agents", data)
        self.assert_in("mode", data)
        self.assert_equal(len(data["agents"]), 9, "Should have 9 agents")
        
        # Check that all expected agents are present
        agent_names = [agent["name"] for agent in data["agents"]]
        expected_agents = [
            "SQL Generator",
            "SQL Reviewer", 
            "SQL Executor",
            "Data Analysis Agent",
            "Data Visualization Agent",
            "Data Question Agent",
            "Alternative Visualization Agent",
            "Follow-up Questions Agent",
            "Orchestration Agent"
        ]
        
        for expected_agent in expected_agents:
            self.assert_in(expected_agent, agent_names, f"Missing agent: {expected_agent}")

    # SQL endpoint tests
    def test_sql_generator(self):
        """Test SQL generator endpoint"""
        payload = {
            "user_input": "Show me all data from test table",
            "db_schema": "test schema"
        }
        
        response = client.post("/agents/sql-generator", json=payload)
        # Should either work (200) or return 503 if CrewAI not available
        self.assert_true(response.status_code in [200, 503], 
                        f"Expected 200 or 503, got {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.assert_true(data["success"])
            self.assert_in("data", data)
    
    def test_sql_reviewer(self):
        """Test SQL reviewer endpoint"""
        payload = {
            "sql_query": "SELECT * FROM test_table;",
            "db_schema": "test schema"
        }
        
        response = client.post("/agents/sql-reviewer", json=payload)
        # Should either work (200) or return 503 if CrewAI not available
        self.assert_true(response.status_code in [200, 503], 
                        f"Expected 200 or 503, got {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.assert_true(data["success"])
            self.assert_in("data", data)
    
    def test_sql_executor_missing_db(self):
        """Test SQL executor with nonexistent database"""
        payload = {
            "sql_query": "SELECT * FROM test;"
        }
        
        response = client.post("/agents/execute-sql", json=payload)
        # Should return 404 for missing database
        self.assert_equal(response.status_code, 404)

    # Analysis endpoint tests
    def test_data_analysis(self):
        """Test data analysis endpoint"""
        payload = {
            "columns": "id,name,value",
            "shape": "100x3",
            "dtypes": "int,str,float",
            "sample_data": '{"id": 1, "name": "test", "value": 100}',
            "user_query": "Analyze this data"
        }
        
        response = client.post("/agents/data-analysis", json=payload)
        # Should either work (200) or return 503 if CrewAI not available
        self.assert_true(response.status_code in [200, 503], 
                        f"Expected 200 or 503, got {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.assert_true(data["success"])
            self.assert_in("data", data)
    
    def test_data_visualization(self):
        """Test data visualization endpoint"""
        payload = {
            "data": '{"name": ["A", "B"], "value": [1, 2]}',
            "user_query": "Create a chart",
            "recommended_viz": "bar chart",
            "analysis": "Test analysis",
            "key_findings": "Test findings"
        }
        
        response = client.post("/agents/data-visualization", json=payload)
        # Should either work (200) or return 503 if CrewAI not available
        self.assert_true(response.status_code in [200, 503], 
                        f"Expected 200 or 503, got {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.assert_true(data["success"])
            self.assert_in("data", data)

    # Interaction endpoint tests
    def test_orchestration(self):
        """Test orchestration endpoint"""
        payload = {
            "user_input": "Show me sales data",
            "previous_context": ""
        }
        
        response = client.post("/agents/orchestration", json=payload)
        # Should either work (200) or return 503 if CrewAI not available
        self.assert_true(response.status_code in [200, 503], 
                        f"Expected 200 or 503, got {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.assert_true(data["success"])
            self.assert_in("data", data)
    
    def test_data_question(self):
        """Test data question endpoint"""
        payload = {
            "user_question": "What does this data mean?",
            "current_data": '{"values": [1, 2, 3]}',
            "data_summary": "Test summary",
            "chart_info": "Bar chart showing values"
        }
        
        response = client.post("/agents/data-question", json=payload)
        # Should either work (200) or return 503 if CrewAI not available
        self.assert_true(response.status_code in [200, 503], 
                        f"Expected 200 or 503, got {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.assert_true(data["success"])
            self.assert_in("data", data)
    
    def test_alternative_visualization(self):
        """Test alternative visualization endpoint"""
        payload = {
            "user_request": "Show this as a scatter plot",
            "current_data": '{"x": [1, 2], "y": [3, 4]}',
            "current_chart_type": "bar"
        }
        
        response = client.post("/agents/alternative-visualization", json=payload)
        # Should either work (200) or return 503 if CrewAI not available
        self.assert_true(response.status_code in [200, 503], 
                        f"Expected 200 or 503, got {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.assert_true(data["success"])
            self.assert_in("data", data)
    
    def test_follow_up_questions(self):
        """Test follow-up questions endpoint"""
        payload = {
            "analysis": "Test analysis results",
            "original_query": "Show me the data",
            "key_findings": "Key finding 1, Key finding 2",
            "db_schema": "test schema"
        }
        
        response = client.post("/agents/follow-up-questions", json=payload)
        # Should either work (200) or return 503 if CrewAI not available
        self.assert_true(response.status_code in [200, 503], 
                        f"Expected 200 or 503, got {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.assert_true(data["success"])
            self.assert_in("data", data)

    # Error handling tests
    def test_missing_field_validation(self):
        """Test validation errors for missing required fields"""
        payload = {
            "user_input": "test query"
            # Missing db_schema
        }
        
        response = client.post("/agents/sql-generator", json=payload)
        self.assert_equal(response.status_code, 422, "Should return validation error")
    
    def test_orchestration_missing_input(self):
        """Test orchestration with missing user input"""
        payload = {
            "previous_context": "some context"
            # Missing user_input
        }
        
        response = client.post("/agents/orchestration", json=payload)
        # Should return 400 for missing user_input or 503 if CrewAI not available
        self.assert_true(response.status_code in [400, 503], 
                        f"Expected 400 or 503, got {response.status_code}")

def main():
    """Main test runner"""
    try:
        runner = TestRunner()
        success = runner.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
