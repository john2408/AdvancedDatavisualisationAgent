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
