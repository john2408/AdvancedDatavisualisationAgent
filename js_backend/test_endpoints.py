"""
Unit tests for FastAPI backend endpoints
Tests all agent endpoints and basic functionality
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the agents import before importing main
mock_crew = MagicMock()
mock_crew.kickoff.return_value = MagicMock()
mock_crew.kickoff.return_value.pydantic = MagicMock()

with patch.dict('sys.modules', {
    'agents.crew_agents': MagicMock(
        sql_generator_crew=mock_crew,
        sql_reviewer_crew=mock_crew,
        data_analysis_crew=mock_crew,
        data_visualization_crew=mock_crew,
        orchestration_crew=mock_crew,
        data_question_crew=mock_crew,
        alternative_viz_crew=mock_crew,
        follow_up_crew=mock_crew
    )
}):
    from main import app

client = TestClient(app)

class TestBasicEndpoints:
    """Test basic API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["status"] == "active"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
    
    def test_config_schema(self):
        """Test config schema endpoint"""
        response = client.get("/config/schema")
        assert response.status_code == 200
        data = response.json()
        assert "db_schema_agent" in data
        assert "db_schema_user" in data
        assert "db_path" in data
    
    def test_agents_list(self):
        """Test agents list endpoint"""
        response = client.get("/agents/list")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "mode" in data
        assert len(data["agents"]) == 9  # Should have 9 agents
        
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
            assert expected_agent in agent_names

class TestSQLEndpoints:
    """Test SQL-related endpoints"""
    
    @patch('main.sql_generator_crew')
    def test_sql_generator(self, mock_sql_gen):
        """Test SQL generator endpoint"""
        # Mock the crew response
        mock_result = MagicMock()
        mock_result.pydantic.sqlquery = "SELECT * FROM test_table;"
        mock_sql_gen.kickoff.return_value = mock_result
        
        payload = {
            "user_input": "Show me all data from test table",
            "db_schema": "test schema"
        }
        
        response = client.post("/agents/sql-generator", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sqlquery" in data["data"]
        assert data["data"]["agent_type"] == "sql_generator"
    
    @patch('main.sql_reviewer_crew')
    def test_sql_reviewer(self, mock_sql_reviewer):
        """Test SQL reviewer endpoint"""
        # Mock the crew response
        mock_result = MagicMock()
        mock_result.pydantic.reviewed_sqlquery = "SELECT * FROM test_table WHERE id > 0;"
        mock_sql_reviewer.kickoff.return_value = mock_result
        
        payload = {
            "sql_query": "SELECT * FROM test_table;",
            "db_schema": "test schema"
        }
        
        response = client.post("/agents/sql-reviewer", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reviewed_sqlquery" in data["data"]
        assert data["data"]["agent_type"] == "sql_reviewer"
    
    @patch('main.sqlite3')
    @patch('main.pd')
    @patch('main.os.path.exists')
    def test_sql_executor(self, mock_exists, mock_pd, mock_sqlite):
        """Test SQL executor endpoint"""
        # Mock database connection and pandas
        mock_exists.return_value = True
        mock_conn = MagicMock()
        mock_sqlite.connect.return_value = mock_conn
        
        # Mock pandas DataFrame
        mock_df = MagicMock()
        mock_df.to_dict.return_value = [{"id": 1, "name": "test"}]
        mock_df.columns.tolist.return_value = ["id", "name"]
        mock_df.__len__ = lambda x: 1
        mock_pd.read_sql_query.return_value = mock_df
        
        payload = {
            "sql_query": "SELECT * FROM test_table;"
        }
        
        response = client.post("/agents/execute-sql", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "results" in data["data"]
        assert "metadata" in data["data"]

class TestDataAnalysisEndpoints:
    """Test data analysis endpoints"""
    
    @patch('main.data_analysis_crew')
    def test_data_analysis(self, mock_analysis):
        """Test data analysis endpoint"""
        # Mock the crew response
        mock_result = MagicMock()
        mock_result.pydantic.analysis = "Test analysis"
        mock_result.pydantic.recommended_visualizations = "bar chart"
        mock_result.pydantic.key_findings = "Test findings"
        mock_analysis.kickoff.return_value = mock_result
        
        payload = {
            "columns": "id,name,value",
            "shape": "100x3",
            "dtypes": "int,str,float",
            "sample_data": '{"id": 1, "name": "test", "value": 100}',
            "user_query": "Analyze this data"
        }
        
        response = client.post("/agents/data-analysis", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "analysis" in data["data"]
        assert data["data"]["agent_type"] == "data_analysis"
    
    @patch('main.data_visualization_crew')
    def test_data_visualization(self, mock_viz):
        """Test data visualization endpoint"""
        # Mock the crew response
        mock_result = MagicMock()
        mock_result.pydantic.plot_type = "bar"
        mock_result.pydantic.x_column = "name"
        mock_result.pydantic.y_column = "value"
        mock_result.pydantic.color_column = None
        mock_result.pydantic.title = "Test Chart"
        mock_result.pydantic.plot_spec = {"type": "bar"}
        mock_viz.kickoff.return_value = mock_result
        
        payload = {
            "data": '{"name": ["A", "B"], "value": [1, 2]}',
            "user_query": "Create a chart",
            "recommended_viz": "bar chart",
            "analysis": "Test analysis",
            "key_findings": "Test findings"
        }
        
        response = client.post("/agents/data-visualization", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "plot_type" in data["data"]
        assert data["data"]["agent_type"] == "data_visualization"

class TestInteractionEndpoints:
    """Test user interaction endpoints"""
    
    @patch('main.orchestration_crew')
    def test_orchestration(self, mock_orchestration):
        """Test orchestration endpoint"""
        # Mock the crew response
        mock_result = MagicMock()
        mock_result.action_type = "new_query"
        mock_result.reasoning = "This is a new data request"
        mock_result.confidence = 0.95
        mock_orchestration.kickoff.return_value.pydantic = mock_result
        
        payload = {
            "user_input": "Show me sales data",
            "previous_context": ""
        }
        
        response = client.post("/agents/orchestration", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "action_type" in data["data"]
        assert data["data"]["agent_type"] == "orchestration"
    
    @patch('main.data_question_crew')
    def test_data_question(self, mock_question):
        """Test data question endpoint"""
        # Mock the crew response
        mock_result = MagicMock()
        mock_result.pydantic.answer = "The data shows..."
        mock_result.pydantic.referenced_data_points = ["point1", "point2"]
        mock_result.pydantic.insights = ["insight1", "insight2"]
        mock_question.kickoff.return_value = mock_result
        
        payload = {
            "user_question": "What does this data mean?",
            "current_data": '{"values": [1, 2, 3]}',
            "data_summary": "Test summary",
            "chart_info": "Bar chart showing values"
        }
        
        response = client.post("/agents/data-question", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "answer" in data["data"]
        assert data["data"]["agent_type"] == "data_question"
    
    @patch('main.alternative_viz_crew')
    def test_alternative_visualization(self, mock_alt_viz):
        """Test alternative visualization endpoint"""
        # Mock the crew response
        mock_result = MagicMock()
        mock_result.pydantic.plot_type = "scatter"
        mock_result.pydantic.x_column = "x"
        mock_result.pydantic.y_column = "y"
        mock_result.pydantic.color_column = None
        mock_result.pydantic.title = "Alternative Chart"
        mock_result.pydantic.plot_spec = {"type": "scatter"}
        mock_alt_viz.kickoff.return_value = mock_result
        
        payload = {
            "user_request": "Show this as a scatter plot",
            "current_data": '{"x": [1, 2], "y": [3, 4]}',
            "current_chart_type": "bar"
        }
        
        response = client.post("/agents/alternative-visualization", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "plot_type" in data["data"]
        assert data["data"]["agent_type"] == "alternative_visualization"
    
    @patch('main.follow_up_crew')
    def test_follow_up_questions(self, mock_follow_up):
        """Test follow-up questions endpoint"""
        # Mock the crew response
        mock_result = MagicMock()
        mock_result.pydantic.questions = ["Question 1?", "Question 2?"]
        mock_result.pydantic.categories = ["category1", "category2"]
        mock_follow_up.kickoff.return_value = mock_result
        
        payload = {
            "analysis": "Test analysis results",
            "original_query": "Show me the data",
            "key_findings": "Key finding 1, Key finding 2",
            "db_schema": "test schema"
        }
        
        response = client.post("/agents/follow-up-questions", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "questions" in data["data"]
        assert data["data"]["agent_type"] == "follow_up_questions"

class TestErrorHandling:
    """Test error handling for endpoints"""
    
    def test_sql_generator_missing_fields(self):
        """Test SQL generator with missing required fields"""
        payload = {
            "user_input": "test query"
            # Missing db_schema
        }
        
        response = client.post("/agents/sql-generator", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_sql_executor_nonexistent_db(self):
        """Test SQL executor with nonexistent database"""
        with patch('main.os.path.exists', return_value=False):
            payload = {
                "sql_query": "SELECT * FROM test;"
            }
            
            response = client.post("/agents/execute-sql", json=payload)
            assert response.status_code == 404
    
    def test_orchestration_missing_input(self):
        """Test orchestration with missing user input"""
        payload = {
            "previous_context": "some context"
            # Missing user_input
        }
        
        response = client.post("/agents/orchestration", json=payload)
        assert response.status_code == 400

def run_tests():
    """Run all tests and provide summary"""
    import subprocess
    import sys
    
    print("🧪 Running comprehensive endpoint tests...")
    print("=" * 60)
    
    # Run pytest with verbose output
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            __file__, 
            "-v", 
            "--tb=short",
            "--no-header"
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print(result.stdout)
        if result.stderr:
            print("ERRORS:")
            print(result.stderr)
        
        print("=" * 60)
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
