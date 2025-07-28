"""
FastAPI Backend with CrewAI Agent Integration
This version integrates with CrewAI agents for real SQL generation and analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import traceback
import yaml
import os

# Import CrewAI agents for real functionality
try:
    from agents.crew_agents import (
        sql_generator_crew, 
        sql_reviewer_crew, 
        data_analysis_crew,
        data_visualization_crew,
        orchestration_crew,
        data_question_crew,
        alternative_viz_crew,
        follow_up_crew
    )
    CREW_AI_AVAILABLE = True
    print("✅ CrewAI agents loaded successfully")
except ImportError as e:
    print(f"⚠️ Warning: CrewAI agents not available: {e}")
    CREW_AI_AVAILABLE = False

app = FastAPI(
    title="Advanced Data Visualization Agent API",
    description="FastAPI backend for data visualization and analysis",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
def load_config():
    """Load configuration from config.yaml file"""
    config_path = "/app/config.yaml"  # Docker path
    if not os.path.exists(config_path):
        config_path = "../config.yaml"  # Local development path
        if not os.path.exists(config_path):
            config_path = "config.yaml"  # Current directory
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Warning: Could not load config.yaml: {e}")
        return {
            "db_path": "data/registered_vehicles.sqlite",
            "db_schema_agent": "Mock database schema for testing",
            "db_schema_user": "Mock user-friendly schema for testing"
        }

config = load_config()

# Request/Response Models
class SQLGeneratorRequest(BaseModel):
    user_input: str = Field(..., description="Natural language query from user")
    db_schema: str = Field(..., description="Database schema information")

class APIResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Advanced Data Visualization Agent API", "status": "active"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "FastAPI backend is running"}

@app.get("/config/schema")
async def get_database_schema():
    """Get database schema for frontend"""
    return {
        "db_schema_agent": config.get("db_schema_agent", "Schema not available"),
        "db_schema_user": config.get("db_schema_user", "User schema not available"),
        "db_path": config.get("db_path", "data/registered_vehicles.sqlite")
    }

@app.post("/agents/sql-generator")

@app.post("/agents/sql-generator", response_model=APIResponse)
async def generate_sql(request: SQLGeneratorRequest):
    """Generate SQL query from natural language input using CrewAI agents"""
    try:
        if not CREW_AI_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="CrewAI agents are not available. Please check the server configuration and ensure all dependencies are installed."
            )
        
        # Load config to get DB schema
        config = load_config()
        db_schema = config.get('db_schema_agent', '')
        
        if not db_schema:
            raise HTTPException(
                status_code=500,
                detail="Database schema not found in configuration. Please check config.yaml file."
            )
        
        # Use CrewAI SQL generator crew
        print(f"🤖 Generating SQL for query: {request.user_input}")
        gen_output = sql_generator_crew.kickoff(inputs={
            "user_input": request.user_input, 
            "db_schema": db_schema
        })
        
        # Extract SQL from crew output
        generated_sql = gen_output.pydantic.sqlquery if hasattr(gen_output, 'pydantic') else str(gen_output)
        
        print(f"✅ Generated SQL: {generated_sql}")
        
        return APIResponse(
            success=True,
            data={
                "sqlquery": generated_sql,
                "agent_type": "sql_generator",
                "mode": "crewai"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ SQL generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SQL generation failed: {str(e)}")

@app.post("/agents/orchestration", response_model=APIResponse)
async def orchestrate_intent(request: dict):
    """Determine user intent using CrewAI orchestration agent"""
    try:
        if not CREW_AI_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="CrewAI orchestration agent is not available. Please check the server configuration and ensure all dependencies are installed."
            )
        
        # Extract user input from request
        user_input = request.get('user_input', '')
        conversation_history = request.get('previous_context', '')
        
        if not user_input:
            raise HTTPException(
                status_code=400,
                detail="user_input is required for orchestration"
            )
        
        # Use CrewAI orchestration crew
        print(f"🎯 Orchestrating intent for: {user_input}")
        orchestration_output = orchestration_crew.kickoff(inputs={
            "user_query": user_input,
            "conversation_history": conversation_history,
            "current_data_context": ""  # Empty for now, could be populated with current data context
        })
        
        # Extract orchestration result
        result = orchestration_output.pydantic if hasattr(orchestration_output, 'pydantic') else None
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to get valid response from orchestration agent"
            )
        
        return APIResponse(
            success=True,
            data={
                "action_type": result.action_type,
                "reasoning": result.reasoning,
                "confidence": result.confidence,
                "agent_type": "orchestration",
                "mode": "crewai"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Orchestration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Intent orchestration failed: {str(e)}")

# SQL Execution endpoint
class SQLExecutionRequest(BaseModel):
    sql_query: str = Field(..., description="SQL query to execute")

@app.post("/agents/execute-sql", response_model=APIResponse)
async def execute_sql_query(request: SQLExecutionRequest):
    """Execute SQL query against the database and return results"""
    try:
        import sqlite3
        import pandas as pd
        
        # Get database path from config
        config = load_config()
        db_path = config.get('db_path', 'data/registered_vehicles.sqlite')
        
        if not os.path.exists(db_path):
            raise HTTPException(
                status_code=404,
                detail=f"Database file not found at: {db_path}"
            )
        
        # Execute SQL query
        conn = sqlite3.connect(db_path)
        try:
            df = pd.read_sql_query(request.sql_query, conn)
            
            # Convert DataFrame to list of dictionaries
            data = df.to_dict('records')
            
            # Add metadata
            metadata = {
                'row_count': len(data),
                'column_count': len(df.columns) if len(data) > 0 else 0,
                'columns': df.columns.tolist() if len(data) > 0 else []
            }
            
            return APIResponse(
                success=True,
                data={
                    'results': data,
                    'metadata': metadata,
                    'sql_query': request.sql_query
                }
            )
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"❌ SQL execution failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"SQL execution failed: {str(e)}"
        )

# SQL Review endpoint
class SQLReviewRequest(BaseModel):
    sql_query: str = Field(..., description="SQL query to review")
    db_schema: str = Field(..., description="Database schema for context")

@app.post("/agents/sql-reviewer", response_model=APIResponse)
async def review_sql_query(request: SQLReviewRequest):
    """Review and optimize SQL query using GPT-4o reviewer agent"""
    try:
        if not CREW_AI_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="CrewAI agents are not available"
            )
        
        result = sql_reviewer_crew.kickoff(inputs={
            "sql_query": request.sql_query,
            "db_schema": request.db_schema
        })
        
        if not result or not hasattr(result, 'pydantic'):
            raise HTTPException(
                status_code=500,
                detail="Failed to get valid response from SQL reviewer agent"
            )
        
        return APIResponse(
            success=True,
            data={
                "reviewed_sqlquery": result.pydantic.reviewed_sqlquery,
                "agent_type": "sql_reviewer",
                "mode": "crewai"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ SQL review failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SQL review failed: {str(e)}")

# Data Analysis endpoint
class DataAnalysisRequest(BaseModel):
    columns: str = Field(..., description="Column names of the data")
    shape: str = Field(..., description="Shape of the data (rows x columns)")
    dtypes: str = Field(..., description="Data types of columns")
    sample_data: str = Field(..., description="Sample data as JSON string")
    user_query: str = Field(..., description="Original user query")

@app.post("/agents/data-analysis", response_model=APIResponse)
async def analyze_data(request: DataAnalysisRequest):
    """Analyze data patterns and recommend visualizations"""
    try:
        if not CREW_AI_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="CrewAI agents are not available"
            )
        
        result = data_analysis_crew.kickoff(inputs={
            "columns": request.columns,
            "shape": request.shape,
            "dtypes": request.dtypes,
            "sample_data": request.sample_data,
            "user_query": request.user_query
        })
        
        if not result or not hasattr(result, 'pydantic'):
            raise HTTPException(
                status_code=500,
                detail="Failed to get valid response from data analysis agent"
            )
        
        return APIResponse(
            success=True,
            data={
                "analysis": result.pydantic.analysis,
                "recommended_visualizations": result.pydantic.recommended_visualizations,
                "key_findings": result.pydantic.key_findings,
                "agent_type": "data_analysis",
                "mode": "crewai"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Data analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data analysis failed: {str(e)}")

# Data Visualization endpoint
class VisualizationRequest(BaseModel):
    data: str = Field(..., description="Data as JSON string")
    user_query: str = Field(..., description="Original user query")
    recommended_viz: str = Field(..., description="Recommended visualization type")
    analysis: str = Field(..., description="Data analysis results")
    key_findings: str = Field(..., description="Key findings from analysis")

@app.post("/agents/data-visualization", response_model=APIResponse)
async def create_visualization(request: VisualizationRequest):
    """Create visualization using data visualization agent"""
    try:
        if not CREW_AI_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="CrewAI agents are not available"
            )
        
        result = data_visualization_crew.kickoff(inputs={
            "data": request.data,
            "user_query": request.user_query,
            "recommended_viz": request.recommended_viz,
            "analysis": request.analysis,
            "key_findings": request.key_findings
        })
        
        if not result or not hasattr(result, 'pydantic'):
            raise HTTPException(
                status_code=500,
                detail="Failed to get valid response from visualization agent"
            )
        
        return APIResponse(
            success=True,
            data={
                "plot_type": result.pydantic.plot_type,
                "x_column": result.pydantic.x_column,
                "y_column": result.pydantic.y_column,
                "color_column": result.pydantic.color_column,
                "title": result.pydantic.title,
                "plot_spec": result.pydantic.plot_spec,
                "agent_type": "data_visualization",
                "mode": "crewai"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Visualization creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Visualization creation failed: {str(e)}")

# Data Question Answering endpoint
class DataQuestionRequest(BaseModel):
    user_question: str = Field(..., description="User's question about the data")
    current_data: str = Field(..., description="Current data as JSON string")
    data_summary: str = Field(..., description="Summary of the data")
    chart_info: str = Field(..., description="Information about current chart")

@app.post("/agents/data-question", response_model=APIResponse)
async def answer_data_question(request: DataQuestionRequest):
    """Answer questions about current data using data question agent"""
    try:
        if not CREW_AI_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="CrewAI agents are not available"
            )
        
        result = data_question_crew.kickoff(inputs={
            "user_question": request.user_question,
            "current_data": request.current_data,
            "data_summary": request.data_summary,
            "chart_info": request.chart_info
        })
        
        if not result or not hasattr(result, 'pydantic'):
            raise HTTPException(
                status_code=500,
                detail="Failed to get valid response from data question agent"
            )
        
        return APIResponse(
            success=True,
            data={
                "answer": result.pydantic.answer,
                "referenced_data_points": result.pydantic.referenced_data_points,
                "insights": result.pydantic.insights,
                "agent_type": "data_question",
                "mode": "crewai"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Data question answering failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data question answering failed: {str(e)}")

# Alternative Visualization endpoint
class AlternativeVisualizationRequest(BaseModel):
    user_request: str = Field(..., description="User's request for alternative visualization")
    current_data: str = Field(..., description="Current data as JSON string")
    current_chart_type: str = Field(..., description="Current chart type")

@app.post("/agents/alternative-visualization", response_model=APIResponse)
async def create_alternative_visualization(request: AlternativeVisualizationRequest):
    """Create alternative visualization using alternative viz agent"""
    try:
        if not CREW_AI_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="CrewAI agents are not available"
            )
        
        result = alternative_viz_crew.kickoff(inputs={
            "user_request": request.user_request,
            "current_data": request.current_data,
            "current_chart_type": request.current_chart_type
        })
        
        if not result or not hasattr(result, 'pydantic'):
            raise HTTPException(
                status_code=500,
                detail="Failed to get valid response from alternative visualization agent"
            )
        
        return APIResponse(
            success=True,
            data={
                "plot_type": result.pydantic.plot_type,
                "x_column": result.pydantic.x_column,
                "y_column": result.pydantic.y_column,
                "color_column": result.pydantic.color_column,
                "title": result.pydantic.title,
                "plot_spec": result.pydantic.plot_spec,
                "agent_type": "alternative_visualization",
                "mode": "crewai"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Alternative visualization creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Alternative visualization creation failed: {str(e)}")

# Follow-up Questions endpoint
class FollowUpRequest(BaseModel):
    analysis: str = Field(..., description="Data analysis results")
    original_query: str = Field(..., description="Original user query")
    key_findings: str = Field(..., description="Key findings from analysis")
    db_schema: str = Field(..., description="Database schema for context")

@app.post("/agents/follow-up-questions", response_model=APIResponse)
async def generate_follow_up_questions(request: FollowUpRequest):
    """Generate follow-up questions using follow-up agent"""
    try:
        if not CREW_AI_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="CrewAI agents are not available"
            )
        
        result = follow_up_crew.kickoff(inputs={
            "analysis": request.analysis,
            "original_query": request.original_query,
            "key_findings": request.key_findings,
            "db_schema": request.db_schema
        })
        
        if not result or not hasattr(result, 'pydantic'):
            raise HTTPException(
                status_code=500,
                detail="Failed to get valid response from follow-up questions agent"
            )
        
        return APIResponse(
            success=True,
            data={
                "questions": result.pydantic.questions,
                "categories": result.pydantic.categories,
                "agent_type": "follow_up_questions",
                "mode": "crewai"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Follow-up questions generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Follow-up questions generation failed: {str(e)}")

@app.get("/agents/list")
async def list_available_agents():
    """List all available AI agents and their endpoints"""
    if not CREW_AI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="CrewAI agents are not available. Please check the server configuration and ensure all dependencies are installed."
        )
    
    return {
        "agents": [
            {
                "name": "SQL Generator",
                "endpoint": "/agents/sql-generator",
                "description": "Converts natural language to SQL queries",
                "status": "active"
            },
            {
                "name": "SQL Reviewer",
                "endpoint": "/agents/sql-reviewer",
                "description": "Reviews and optimizes SQL queries",
                "status": "active"
            },
            {
                "name": "SQL Executor",
                "endpoint": "/agents/execute-sql",
                "description": "Executes SQL queries against the database",
                "status": "active"
            },
            {
                "name": "Data Analysis Agent",
                "endpoint": "/agents/data-analysis",
                "description": "Analyzes data patterns and recommends visualizations",
                "status": "active"
            },
            {
                "name": "Data Visualization Agent",
                "endpoint": "/agents/data-visualization",
                "description": "Creates visualizations from data",
                "status": "active"
            },
            {
                "name": "Data Question Agent",
                "endpoint": "/agents/data-question",
                "description": "Answers questions about current data",
                "status": "active"
            },
            {
                "name": "Alternative Visualization Agent",
                "endpoint": "/agents/alternative-visualization",
                "description": "Creates alternative visualizations",
                "status": "active"
            },
            {
                "name": "Follow-up Questions Agent",
                "endpoint": "/agents/follow-up-questions",
                "description": "Generates relevant follow-up questions",
                "status": "active"
            },
            {
                "name": "Orchestration Agent", 
                "endpoint": "/agents/orchestration",
                "description": "Determines user intent and routes requests",
                "status": "active"
            }
        ],
        "mode": "crewai",
        "message": "Running with CrewAI agents"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
