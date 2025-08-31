"""
This module implements the fast chart type selection using heuristics + optional LLM fallback.
Replaces the slow visualization agent with deterministic logic.
"""

import pandas as pd
import re
import json
from typing import List, Optional, Dict, Set
from pydantic import BaseModel
from enum import Enum

# Import CrewAI components for the sophisticated agent fallback
from agents.crew_agents import chart_type_crew
from pydantic import BaseModel
from enum import Enum

class ChartType(Enum):
    """Supported chart types."""
    BAR = "BAR"
    STACKED_BAR = "STACKED_BAR"
    LINE = "LINE"
    MULTI_LINE = "MULTI_LINE"
    PIE = "PIE"
    SCATTER = "SCATTER"
    HISTOGRAM = "HISTOGRAM"
    BOX = "BOX"
    HEATMAP = "HEATMAP"

class ChartPlan(BaseModel):
    """Chart plan model for deterministic plot building."""
    chart_type: str
    x: str
    y: List[str]
    color: Optional[str] = None
    aggregation: str = "sum"
    transform: Optional[str] = None
    title: Optional[str] = None


def analyze_dataframe_structure(df: pd.DataFrame) -> Dict:
    """
    Analyze DataFrame structure to identify column types and characteristics.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary with DataFrame analysis including numeric, categorical, and date columns
    """
    analysis = {
        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist(),
        'date_columns': [],
        'row_count': len(df),
        'column_count': len(df.columns),
        'has_nulls': df.isnull().any().any(),
        'categorical_cardinality': {}
    }
    
    # Detect datetime columns first
    datetime_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
    analysis['date_columns'].extend(datetime_columns)
    
    # Remove datetime columns from categorical columns
    analysis['categorical_columns'] = [col for col in analysis['categorical_columns'] 
                                     if col not in datetime_columns]
    
    # Detect potential date columns among string columns
    for col in analysis['categorical_columns'][:]:  # Use slice copy to avoid modification during iteration
        if df[col].dtype == 'object':
            # Simple date pattern detection
            sample_values = df[col].dropna().head(5).astype(str)
            if any(re.match(r'\d{4}-\d{2}', str(val)) for val in sample_values):
                analysis['date_columns'].append(col)
                analysis['categorical_columns'].remove(col)
    
    # Calculate cardinality for categorical columns
    for col in analysis['categorical_columns']:
        analysis['categorical_cardinality'][col] = df[col].nunique()
    
    return analysis


def return_chart_type(user_query: str, data: pd.DataFrame):
    "Get the most suitable chart type based on user query and data context."
    
    # Get data analysis and convert to serializable format
    data_analysis = analyze_dataframe_structure(data)
    
    # Convert numpy types to native Python types for CrewAI serialization
    serializable_analysis = {
        'numeric_columns': data_analysis['numeric_columns'],
        'categorical_columns': data_analysis['categorical_columns'], 
        'date_columns': data_analysis['date_columns'],
        'row_count': int(data_analysis['row_count']),
        'column_count': int(data_analysis['column_count']),
        'has_nulls': bool(data_analysis['has_nulls']),  # Convert numpy bool to Python bool
        'categorical_cardinality': {k: int(v) for k, v in data_analysis['categorical_cardinality'].items()}
    }

    chart_type_output = chart_type_crew.kickoff(inputs={
        "user_query": user_query,
        "data_analysis": serializable_analysis
    })

    return chart_type_output.pydantic.chart_type



def create_chart_plan(df: pd.DataFrame, user_query: str) -> ChartPlan:
    """
    Create a comprehensive chart plan using the chart_type_crew agent for intelligent chart type selection.
    
    Args:
        df: Input DataFrame
        user_query: User's natural language request
        
    Returns:
        ChartPlan with optimal chart type and column assignments
    """
    # Get chart type from the intelligent agent
    chart_type = return_chart_type(user_query, df)
    
    # Analyze DataFrame structure for column assignment
    analysis = analyze_dataframe_structure(df)
    
    # Build chart plan based on the selected chart type
    if chart_type == ChartType.BAR.value:
        return _create_bar_chart_plan(analysis)
    elif chart_type == ChartType.STACKED_BAR.value:
        return _create_stacked_bar_chart_plan(analysis)
    elif chart_type == ChartType.LINE.value:
        return _create_line_chart_plan(analysis)
    elif chart_type == ChartType.MULTI_LINE.value:
        return _create_multi_line_chart_plan(analysis)
    elif chart_type == ChartType.PIE.value:
        return _create_pie_chart_plan(analysis)
    elif chart_type == ChartType.SCATTER.value:
        return _create_scatter_chart_plan(analysis)
    elif chart_type == ChartType.HISTOGRAM.value:
        return _create_histogram_chart_plan(analysis)
    elif chart_type == ChartType.BOX.value:
        return _create_box_chart_plan(analysis)
    elif chart_type == ChartType.HEATMAP.value:
        return _create_heatmap_chart_plan(analysis)
    else:
        # Fallback to bar chart if unknown type
        return _create_bar_chart_plan(analysis)


def _create_bar_chart_plan(analysis: Dict) -> ChartPlan:
    """Create a bar chart plan."""
    categorical_cols = analysis['categorical_columns']
    numeric_cols = analysis['numeric_columns']
    
    x_col = categorical_cols[0] if categorical_cols else numeric_cols[0]
    y_col = numeric_cols[0] if numeric_cols else categorical_cols[0]
    
    return ChartPlan(
        chart_type=ChartType.BAR.value,
        x=x_col,
        y=[y_col],
        title=f"{y_col} by {x_col}"
    )


def _create_stacked_bar_chart_plan(analysis: Dict) -> ChartPlan:
    """Create a stacked bar chart plan."""
    categorical_cols = analysis['categorical_columns']
    numeric_cols = analysis['numeric_columns']
    
    x_col = categorical_cols[0] if categorical_cols else numeric_cols[0]
    y_col = numeric_cols[0] if numeric_cols else categorical_cols[1] if len(categorical_cols) > 1 else categorical_cols[0]
    color_col = categorical_cols[1] if len(categorical_cols) > 1 else None
    
    return ChartPlan(
        chart_type=ChartType.STACKED_BAR.value,
        x=x_col,
        y=[y_col],
        color=color_col,
        title=f"{y_col} by {x_col}" + (f" and {color_col}" if color_col else "")
    )


def _create_line_chart_plan(analysis: Dict) -> ChartPlan:
    """Create a line chart plan."""
    date_cols = analysis['date_columns']
    numeric_cols = analysis['numeric_columns']
    categorical_cols = analysis['categorical_columns']
    
    x_col = date_cols[0] if date_cols else categorical_cols[0] if categorical_cols else numeric_cols[0]
    y_col = numeric_cols[0] if numeric_cols else categorical_cols[0]
    
    return ChartPlan(
        chart_type=ChartType.LINE.value,
        x=x_col,
        y=[y_col],
        title=f"{y_col} over {x_col}"
    )


def _create_multi_line_chart_plan(analysis: Dict) -> ChartPlan:
    """Create a multi-line chart plan."""
    date_cols = analysis['date_columns']
    numeric_cols = analysis['numeric_columns']
    categorical_cols = analysis['categorical_columns']
    
    x_col = date_cols[0] if date_cols else categorical_cols[0] if categorical_cols else numeric_cols[0]
    y_col = numeric_cols[0] if numeric_cols else categorical_cols[1] if len(categorical_cols) > 1 else categorical_cols[0]
    color_col = categorical_cols[0] if categorical_cols and x_col != categorical_cols[0] else (
        categorical_cols[1] if len(categorical_cols) > 1 else None
    )
    
    return ChartPlan(
        chart_type=ChartType.MULTI_LINE.value,
        x=x_col,
        y=[y_col],
        color=color_col,
        title=f"{y_col} trends by {color_col} over {x_col}" if color_col else f"{y_col} over {x_col}"
    )


def _create_pie_chart_plan(analysis: Dict) -> ChartPlan:
    """Create a pie chart plan."""
    categorical_cols = analysis['categorical_columns']
    numeric_cols = analysis['numeric_columns']
    
    x_col = categorical_cols[0] if categorical_cols else numeric_cols[0]
    y_col = numeric_cols[0] if numeric_cols else categorical_cols[1] if len(categorical_cols) > 1 else categorical_cols[0]
    
    return ChartPlan(
        chart_type=ChartType.PIE.value,
        x=x_col,
        y=[y_col],
        transform="percentage",
        title=f"{x_col} Distribution (%)"
    )


def _create_scatter_chart_plan(analysis: Dict) -> ChartPlan:
    """Create a scatter chart plan."""
    numeric_cols = analysis['numeric_columns']
    categorical_cols = analysis['categorical_columns']
    
    x_col = numeric_cols[0] if len(numeric_cols) > 0 else categorical_cols[0]
    y_col = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0] if numeric_cols else categorical_cols[1] if len(categorical_cols) > 1 else categorical_cols[0]
    color_col = categorical_cols[0] if categorical_cols and analysis['categorical_cardinality'].get(categorical_cols[0], 0) <= 10 else None
    
    return ChartPlan(
        chart_type=ChartType.SCATTER.value,
        x=x_col,
        y=[y_col],
        color=color_col,
        title=f"{y_col} vs {x_col}"
    )


def _create_histogram_chart_plan(analysis: Dict) -> ChartPlan:
    """Create a histogram chart plan."""
    numeric_cols = analysis['numeric_columns']
    
    x_col = numeric_cols[0] if numeric_cols else analysis['categorical_columns'][0]
    
    return ChartPlan(
        chart_type=ChartType.HISTOGRAM.value,
        x=x_col,
        y=[x_col],
        title=f"Distribution of {x_col}"
    )


def _create_box_chart_plan(analysis: Dict) -> ChartPlan:
    """Create a box chart plan."""
    numeric_cols = analysis['numeric_columns']
    categorical_cols = analysis['categorical_columns']
    
    y_col = numeric_cols[0] if numeric_cols else categorical_cols[0]
    x_col = categorical_cols[0] if categorical_cols else "distribution"
    
    return ChartPlan(
        chart_type=ChartType.BOX.value,
        x=x_col,
        y=[y_col],
        title=f"Distribution of {y_col}" + (f" by {x_col}" if x_col != "distribution" else "")
    )


def _create_heatmap_chart_plan(analysis: Dict) -> ChartPlan:
    """Create a heatmap chart plan."""
    numeric_cols = analysis['numeric_columns']
    categorical_cols = analysis['categorical_columns']
    
    # For heatmaps, we typically need two categorical dimensions or a correlation matrix
    if len(categorical_cols) >= 2:
        x_col = categorical_cols[0]
        y_col = categorical_cols[1]
        color_col = numeric_cols[0] if numeric_cols else None
    else:
        # Correlation heatmap
        x_col = numeric_cols[0] if len(numeric_cols) > 0 else categorical_cols[0]
        y_col = numeric_cols[1] if len(numeric_cols) > 1 else categorical_cols[0]
        color_col = None
    
    return ChartPlan(
        chart_type=ChartType.HEATMAP.value,
        x=x_col,
        y=[y_col],
        color=color_col,
        title=f"Heatmap: {y_col} by {x_col}"
    )
