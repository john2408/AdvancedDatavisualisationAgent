"""
Hybrid Visualization Module - Proposal 2 Implementation

This module implements the new step_4_hybrid_visualization function that replaces
the slow visualization agent with fast analytics selector + deterministic plot builder.
"""

import pandas as pd
import streamlit as st
from typing import Dict, Any
from frontend.analytics_selector import create_chart_plan
from frontend.plot_builder import build_figure_from_plan
from frontend.plotly_styles import apply_white_theme_styling


def step_4_hybrid_visualization(query_result: pd.DataFrame, user_query: str) -> Dict[str, Any]:
    """
    New hybrid visualization step that replaces slow agent-based visualization.
    
    Uses Analytics Selector (heuristics + optional LLM) + Deterministic Plot Builder
    for fast, predictable visualization generation.
    
    Args:
        query_result: DataFrame with SQL query results
        user_query: User's original natural language query
        
    Returns:
        Dictionary with visualization results
    """
    try:
        st.info("🧠 Selecting visualization plan...")
        
        # Step 1: Analytics Selector determines chart plan
        plan = create_chart_plan(query_result, user_query)
        
        st.info(f"📐 Plan: {plan.chart_type} (agg={plan.aggregation}" +
                (f", transform={plan.transform}" if plan.transform else "") + ")")
        
        # Step 2: Deterministic Plot Builder creates figure
        fig = build_figure_from_plan(plan, query_result)
        
        # Step 3: Apply consistent white theme styling
        fig = apply_white_theme_styling(fig)
        
        return {
            "success": True,
            "figure": fig,
            "summary": f"{plan.chart_type} visualization generated - {plan.title or 'Chart'}",
            "analysis": f"Chart shows {plan.y[0]} by {plan.x}" + 
                       (f" grouped by {plan.color}" if plan.color else ""),
            "key_findings": [],
            "chart_plan": plan  # Include plan for follow-up processing
        }
        
    except Exception as e:
        st.warning(f"Hybrid visualization failed: {e}")
        return step_4_fallback_visualization(query_result)


def step_4_fallback_visualization(query_result: pd.DataFrame) -> Dict[str, Any]:
    """
    Fallback visualization when hybrid approach fails.
    Creates simple bar chart based on data types.
    """
    try:
        numeric_columns = query_result.select_dtypes(include=['number']).columns.tolist()
        categorical_columns = query_result.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(numeric_columns) >= 1 and len(categorical_columns) >= 1:
            # Simple bar chart fallback
            import plotly.express as px
            
            fig = px.bar(
                query_result,
                x=categorical_columns[0],
                y=numeric_columns[0],
                title="Fallback Visualization",
                color_discrete_sequence=["#1f77b4"]
            )
            
            fig = apply_white_theme_styling(fig)
            
            return {
                "success": True,
                "figure": fig,
                "summary": "Fallback bar chart generated",
                "analysis": f"Simple visualization of {numeric_columns[0]} by {categorical_columns[0]}",
                "key_findings": ["Fallback visualization due to processing error"]
            }
        else:
            # Cannot create meaningful visualization
            return {
                "success": False,
                "figure": None,
                "summary": "Unable to create visualization - insufficient data structure",
                "analysis": "Data does not contain suitable columns for visualization",
                "key_findings": ["Data structure not suitable for standard charts"]
            }
            
    except Exception as fallback_error:
        return {
            "success": False,
            "figure": None,
            "summary": f"Visualization failed: {str(fallback_error)}",
            "analysis": "Both primary and fallback visualization methods failed",
            "key_findings": ["Technical error in visualization generation"]
        }


def generate_alternative_visualization_hybrid(user_request: str, current_data: pd.DataFrame, 
                                            current_chart_context: Dict) -> Dict[str, Any]:
    """
    Generate alternative visualization using hybrid approach for follow-up requests.
    
    Handles requests like:
    - "Convert to pie chart"
    - "Show as percentages"
    - "Make it a line chart"
    
    Args:
        user_request: Follow-up visualization request
        current_data: Current DataFrame
        current_chart_context: Context from previous chart
        
    Returns:
        Dictionary with new visualization results
    """
    try:
        # Modify user request to be more explicit for analytics selector
        enhanced_request = user_request
        
        # Add context hints for better chart selection
        if "convert" in user_request.lower() or "change" in user_request.lower():
            if "pie" in user_request.lower():
                enhanced_request += " - create pie chart with percentage distribution"
            elif "bar" in user_request.lower():
                enhanced_request += " - create bar chart"
            elif "line" in user_request.lower():
                enhanced_request += " - create line chart over time"
        
        if "percentage" in user_request.lower() or "normalize" in user_request.lower():
            enhanced_request += " - show as percentages"
        
        # Use hybrid visualization with enhanced request
        return step_4_hybrid_visualization(current_data, enhanced_request)
        
    except Exception as e:
        st.error(f"Alternative visualization failed: {e}")
        return step_4_fallback_visualization(current_data)
