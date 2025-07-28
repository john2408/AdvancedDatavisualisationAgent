"""
Simplified FastAPI Backend for testing Docker deployment
This version runs without CrewAI dependencies for faster startup
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import traceback

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
    return {"status": "healthy", "service": "ai-agents-api"}

@app.post("/agents/sql-generator", response_model=APIResponse)
async def generate_sql(request: SQLGeneratorRequest):
    """Generate SQL query from natural language input (mock implementation)"""
    try:
        # Mock response for testing
        mock_sql = f"SELECT * FROM vehicles WHERE manufacturer LIKE '%{request.user_input}%' LIMIT 10;"
        
        return APIResponse(
            success=True,
            data={
                "sqlquery": mock_sql,
                "agent_type": "sql_generator",
                "mode": "mock"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL generation failed: {str(e)}")

@app.post("/agents/orchestration", response_model=APIResponse)
async def orchestrate_intent(request: dict):
    """Determine user intent (mock implementation)"""
    try:
        return APIResponse(
            success=True,
            data={
                "action_type": "new_query",
                "reasoning": "Mock orchestration response",
                "confidence": 0.95,
                "agent_type": "orchestration",
                "mode": "mock"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent orchestration failed: {str(e)}")

@app.get("/agents/list")
async def list_available_agents():
    """List all available AI agents and their endpoints"""
    return {
        "agents": [
            {
                "name": "SQL Generator",
                "endpoint": "/agents/sql-generator",
                "description": "Converts natural language to SQL queries",
                "status": "mock"
            },
            {
                "name": "Orchestration Agent",
                "endpoint": "/agents/orchestration",
                "description": "Determines user intent and routes requests",
                "status": "mock"
            }
        ],
        "mode": "mock",
        "message": "Running in mock mode for Docker testing"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
