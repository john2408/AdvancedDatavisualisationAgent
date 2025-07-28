"""
FastAPI Backend for Advanced Data Visualization Agent
Exposes all AI agents from crew_agents.py as REST API endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sys
import os

# Add the parent directory to the path to import from agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

app = FastAPI(
    title="Advanced Data Visualization Agent API",
    description="FastAPI backend exposing AI agents for data visualization and analysis",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class SQLGeneratorRequest(BaseModel):
    user_input: str = Field(..., description="Natural language query from user")
    db_schema: str = Field(..., description="Database schema information")

class SQLReviewerRequest(BaseModel):
    sql_query: str = Field(..., description="SQL query to review")
    db_schema: str = Field(..., description="Database schema information")

class DataAnalysisRequest(BaseModel):
    columns: str = Field(..., description="Column names")
    shape: str = Field(..., description="DataFrame shape")
    dtypes: str = Field(..., description="Data types")
    sample_data: str = Field(..., description="Sample data")
    user_question: str = Field(..., description="User's original question")

class VisualizationRequest(BaseModel):
    dataframe_json: str = Field(..., description="DataFrame as JSON")
    user_question: str = Field(..., description="User's question")
    recommended_visualizations: str = Field(..., description="Recommended viz types")
    analysis_summary: str = Field(..., description="Analysis summary")
    key_findings: List[str] = Field(..., description="Key findings")

class OrchestrationRequest(BaseModel):
    user_query: str = Field(..., description="User's query")
    conversation_history: str = Field(..., description="Conversation history")
    current_data_context: str = Field(..., description="Current data context")

class DataQuestionRequest(BaseModel):
    user_question: str = Field(..., description="User's question about data")
    current_data: str = Field(..., description="Current data context")
    data_summary: str = Field(..., description="Data summary")
    chart_info: str = Field(..., description="Chart information")

class AlternativeVizRequest(BaseModel):
    user_request: str = Field(..., description="User's visualization request")
    current_data: str = Field(..., description="Current data as JSON")
    current_chart_type: str = Field(..., description="Current chart type")

class FollowUpRequest(BaseModel):
    data_analysis: str = Field(..., description="Data analysis")
    original_query: str = Field(..., description="Original query")
    data_insights: str = Field(..., description="Data insights")
    db_schema: str = Field(..., description="Database schema")

# API Response Models
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
    """Generate SQL query from natural language input"""
    try:
        output = sql_generator_crew.kickoff(inputs={
            "user_input": request.user_input,
            "db_schema": request.db_schema
        })
        
        result = output.pydantic
        return APIResponse(
            success=True,
            data={
                "sqlquery": result.sqlquery,
                "agent_type": "sql_generator"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL generation failed: {str(e)}")

@app.post("/agents/sql-reviewer", response_model=APIResponse)
async def review_sql(request: SQLReviewerRequest):
    """Review and optimize SQL query"""
    try:
        output = sql_reviewer_crew.kickoff(inputs={
            "sql_query": request.sql_query,
            "db_schema": request.db_schema
        })
        
        result = output.pydantic
        return APIResponse(
            success=True,
            data={
                "reviewed_sqlquery": result.reviewed_sqlquery,
                "agent_type": "sql_reviewer"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL review failed: {str(e)}")

@app.post("/agents/data-analysis", response_model=APIResponse)
async def analyze_data(request: DataAnalysisRequest):
    """Analyze data and provide insights"""
    try:
        output = data_analysis_crew.kickoff(inputs={
            "columns": request.columns,
            "shape": request.shape,
            "dtypes": request.dtypes,
            "sample_data": request.sample_data,
            "user_question": request.user_question
        })
        
        result = output.pydantic
        return APIResponse(
            success=True,
            data={
                "analysis": result.analysis,
                "recommended_visualizations": result.recommended_visualizations,
                "key_findings": result.key_findings,
                "agent_type": "data_analyst"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data analysis failed: {str(e)}")

@app.post("/agents/visualization", response_model=APIResponse)
async def create_visualization(request: VisualizationRequest):
    """Create visualization specification"""
    try:
        output = data_visualization_crew.kickoff(inputs={
            "dataframe_json": request.dataframe_json,
            "user_question": request.user_question,
            "recommended_visualizations": request.recommended_visualizations,
            "analysis_summary": request.analysis_summary,
            "key_findings": ", ".join(request.key_findings)
        })
        
        result = output.pydantic
        return APIResponse(
            success=True,
            data={
                "plot_type": result.plot_type,
                "x_column": result.x_column,
                "y_column": result.y_column,
                "color_column": result.color_column,
                "title": result.title,
                "aggregation": result.aggregation,
                "transformation": result.transformation,
                "plot_spec": result.plot_spec,
                "agent_type": "visualization"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization creation failed: {str(e)}")

@app.post("/agents/orchestration", response_model=APIResponse)
async def orchestrate_intent(request: OrchestrationRequest):
    """Determine user intent (new query vs follow-up)"""
    try:
        output = orchestration_crew.kickoff(inputs={
            "user_query": request.user_query,
            "conversation_history": request.conversation_history,
            "current_data_context": request.current_data_context
        })
        
        result = output.pydantic
        return APIResponse(
            success=True,
            data={
                "action_type": result.action_type,
                "reasoning": result.reasoning,
                "confidence": result.confidence,
                "agent_type": "orchestration"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent orchestration failed: {str(e)}")

@app.post("/agents/data-question", response_model=APIResponse)
async def answer_data_question(request: DataQuestionRequest):
    """Answer questions about current data"""
    try:
        output = data_question_crew.kickoff(inputs={
            "user_question": request.user_question,
            "current_data": request.current_data,
            "data_summary": request.data_summary,
            "chart_info": request.chart_info
        })
        
        result = output.pydantic
        return APIResponse(
            success=True,
            data={
                "answer": result.answer,
                "referenced_data_points": result.referenced_data_points,
                "insights": result.insights,
                "agent_type": "data_question"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data question answering failed: {str(e)}")

@app.post("/agents/alternative-visualization", response_model=APIResponse)
async def create_alternative_visualization(request: AlternativeVizRequest):
    """Create alternative visualization for current data"""
    try:
        output = alternative_viz_crew.kickoff(inputs={
            "user_request": request.user_request,
            "current_data": request.current_data,
            "current_chart_type": request.current_chart_type
        })
        
        result = output.pydantic
        return APIResponse(
            success=True,
            data={
                "plot_type": result.plot_type,
                "x_column": result.x_column,
                "y_column": result.y_column,
                "color_column": result.color_column,
                "title": result.title,
                "aggregation": result.aggregation,
                "transformation": result.transformation,
                "plot_spec": result.plot_spec,
                "agent_type": "alternative_visualization"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alternative visualization failed: {str(e)}")

@app.post("/agents/follow-up-questions", response_model=APIResponse)
async def generate_follow_up_questions(request: FollowUpRequest):
    """Generate relevant follow-up questions"""
    try:
        output = follow_up_crew.kickoff(inputs={
            "data_analysis": request.data_analysis,
            "original_query": request.original_query,
            "data_insights": request.data_insights,
            "db_schema": request.db_schema
        })
        
        result = output.pydantic
        return APIResponse(
            success=True,
            data={
                "questions": result.questions,
                "categories": result.categories,
                "agent_type": "follow_up"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Follow-up question generation failed: {str(e)}")

@app.get("/agents/list")
async def list_available_agents():
    """List all available AI agents and their endpoints"""
    return {
        "agents": [
            {
                "name": "SQL Generator",
                "endpoint": "/agents/sql-generator",
                "description": "Converts natural language to SQL queries"
            },
            {
                "name": "SQL Reviewer", 
                "endpoint": "/agents/sql-reviewer",
                "description": "Reviews and optimizes SQL queries"
            },
            {
                "name": "Data Analyst",
                "endpoint": "/agents/data-analysis", 
                "description": "Analyzes data patterns and provides insights"
            },
            {
                "name": "Visualization Agent",
                "endpoint": "/agents/visualization",
                "description": "Creates visualization specifications"
            },
            {
                "name": "Orchestration Agent",
                "endpoint": "/agents/orchestration",
                "description": "Determines user intent and routes requests"
            },
            {
                "name": "Data Question Agent",
                "endpoint": "/agents/data-question",
                "description": "Answers questions about current data"
            },
            {
                "name": "Alternative Visualization Agent", 
                "endpoint": "/agents/alternative-visualization",
                "description": "Creates alternative visualizations"
            },
            {
                "name": "Follow-up Questions Agent",
                "endpoint": "/agents/follow-up-questions", 
                "description": "Generates relevant follow-up questions"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
