"""
Deterministic Plot Builder Module 

This module builds Plotly figures from ChartPlan objects without requiring LLM calls.
Provides fast, deterministic visualization generation.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Figure
from typing import List, Dict, Any, Optional
from frontend.analytics_selector import ChartPlan
from frontend.analytics_selector import ChartType



def build_figure_from_plan(plan: ChartPlan, df: pd.DataFrame) -> Figure:
    """
    Main function to build Plotly figure from chart plan.
    
    Args:
        plan: ChartPlan with visualization specifications
        df: Input DataFrame
        
    Returns:
        Plotly Figure object
    """
    # Apply data transformations first
    df_transformed = apply_data_transformations(df, plan)
    
    # Build chart based on type using ChartType enum values
    if plan.chart_type == ChartType.BAR.value:
        fig = build_simple_bar_chart(df_transformed, plan)
    elif plan.chart_type == ChartType.STACKED_BAR.value:
        fig = build_stacked_bar_chart(df_transformed, plan)
    elif plan.chart_type in [ChartType.LINE.value, ChartType.MULTI_LINE.value]:
        fig = build_line_chart(df_transformed, plan)
    elif plan.chart_type == ChartType.PIE.value:
        fig = build_pie_chart(df_transformed, plan)
    elif plan.chart_type == ChartType.SCATTER.value:
        fig = build_scatter_chart(df_transformed, plan)
    elif plan.chart_type == ChartType.HISTOGRAM.value:
        fig = build_histogram_chart(df_transformed, plan)
    elif plan.chart_type == ChartType.BOX.value:
        fig = build_box_chart(df_transformed, plan)
    elif plan.chart_type == ChartType.HEATMAP.value:
        fig = build_heatmap_chart(df_transformed, plan)
    else:
        raise ValueError(f"Unsupported chart type: {plan.chart_type}")

    return fig


def apply_data_transformations(df: pd.DataFrame, plan: ChartPlan) -> pd.DataFrame:
    """
    Apply data transformations based on chart plan.
    
    Args:
        df: Input DataFrame
        plan: Chart plan with transformation specifications
        
    Returns:
        Transformed DataFrame
    """
    df_transformed = df.copy()
    
    if plan.transform == "percentage":
        # Convert values to percentages
        if plan.chart_type == ChartType.PIE.value:
            # For pie charts, calculate percentages of total
            total = df_transformed[plan.y[0]].sum()
            if total > 0:
                df_transformed[f'{plan.y[0]}_pct'] = (df_transformed[plan.y[0]] / total * 100).round(2)
                plan.y = [f'{plan.y[0]}_pct']
        
        elif plan.chart_type == ChartType.STACKED_BAR.value and plan.color:
            # For stacked bars, normalize within each x category
            y_col = plan.y[0]
            df_normalized = []
            
            for x_val in df_transformed[plan.x].unique():
                group_data = df_transformed[df_transformed[plan.x] == x_val].copy()
                total_for_x = group_data[y_col].sum()
                
                if total_for_x > 0:
                    group_data[f'{y_col}_pct'] = (group_data[y_col] / total_for_x * 100).round(2)
                else:
                    group_data[f'{y_col}_pct'] = 0
                
                df_normalized.append(group_data)
            
            df_transformed = pd.concat(df_normalized, ignore_index=True)
            plan.y = [f'{y_col}_pct']
    
    # Top N transformation
    elif plan.transform and plan.transform.startswith('top_'):
        n = int(plan.transform.split('_')[1])
        y_col = plan.y[0]
        
        # Sort by y column and take top N
        df_sorted = df_transformed.sort_values(y_col, ascending=False)
        top_n = df_sorted.head(n-1)  # n-1 because we'll add "Others"
        others = df_sorted.tail(len(df_sorted) - (n-1))
        
        if len(others) > 0:
            # Create "Others" row
            others_row = {plan.x: 'Others', y_col: others[y_col].sum()}
            # Add other columns with appropriate defaults
            for col in df_transformed.columns:
                if col not in others_row:
                    others_row[col] = 'Others' if df_transformed[col].dtype == 'object' else 0
            
            df_transformed = pd.concat([top_n, pd.DataFrame([others_row])], ignore_index=True)
        else:
            df_transformed = top_n
    
    return df_transformed


def build_simple_bar_chart(df: pd.DataFrame, plan: ChartPlan) -> Figure:
    """Build simple bar chart."""
    fig = px.bar(
        df, 
        x=plan.x, 
        y=plan.y[0],
        title=plan.title or f"{plan.y[0]} by {plan.x}",
        color_discrete_sequence=["#1f77b4"]
    )
    return fig


def build_stacked_bar_chart(df: pd.DataFrame, plan: ChartPlan) -> Figure:
    """Build stacked bar chart with color grouping."""
    fig = px.bar(
        df,
        x=plan.x,
        y=plan.y[0], 
        color=plan.color,
        title=plan.title or f"{plan.y[0]} by {plan.x} and {plan.color}",
        color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    )
    
    # Set barmode to stack
    fig.update_layout(barmode="stack")
    
    # If percentage transformation, update y-axis
    if plan.transform == "percentage":
        fig.update_yaxes(title="Percentage (%)", range=[0, 100])
    
    return fig


def build_line_chart(df: pd.DataFrame, plan: ChartPlan) -> Figure:
    """Build line chart."""
    if len(plan.y) == 1:
        # Single line
        fig = px.line(
            df,
            x=plan.x,
            y=plan.y[0],
            title=plan.title or f"{plan.y[0]} over {plan.x}",
            color_discrete_sequence=["#1f77b4"]
        )
        # Add markers to line
        fig.update_traces(mode='lines+markers')
    else:
        # Multiple lines - melt DataFrame for multiple y columns
        df_melted = df.melt(
            id_vars=[plan.x],
            value_vars=plan.y,
            var_name='metric',
            value_name='value'
        )
        
        fig = px.line(
            df_melted,
            x=plan.x,
            y='value',
            color='metric',
            title=plan.title or f"Multiple Metrics over {plan.x}",
            color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
        )
        # Add markers to lines
        fig.update_traces(mode='lines+markers')
    
    return fig


def build_pie_chart(df: pd.DataFrame, plan: ChartPlan) -> Figure:
    """Build pie chart."""
    fig = px.pie(
        df,
        names=plan.x,
        values=plan.y[0],
        title=plan.title or f"{plan.x} Distribution",
        color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    )
    
    # If percentage transformation was applied, show percentages in hover
    if plan.transform == "percentage":
        fig.update_traces(textinfo='label+percent', textposition='inside')
    
    return fig


def build_scatter_chart(df: pd.DataFrame, plan: ChartPlan) -> Figure:
    """Build scatter plot."""
    fig = px.scatter(
        df,
        x=plan.x,
        y=plan.y[0],
        color=plan.color,
        title=plan.title or f"{plan.y[0]} vs {plan.x}",
        color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    )
    return fig


def build_histogram_chart(df: pd.DataFrame, plan: ChartPlan) -> Figure:
    """Build histogram."""
    fig = px.histogram(
        df,
        x=plan.y[0],  # For histogram, y becomes x
        title=plan.title or f"Distribution of {plan.y[0]}",
        color_discrete_sequence=["#1f77b4"]
    )
    return fig


def build_box_chart(df: pd.DataFrame, plan: ChartPlan) -> Figure:
    """Build box plot."""
    fig = px.box(
        df,
        y=plan.y[0],
        title=plan.title or f"Distribution of {plan.y[0]}",
        color_discrete_sequence=["#1f77b4"]
    )
    return fig


def build_heatmap_chart(df: pd.DataFrame, plan: ChartPlan) -> Figure:
    """Build heatmap (correlation matrix or pivot table)."""
    # For numeric columns, create correlation matrix
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            title=plan.title or "Correlation Heatmap",
            color_continuous_scale="RdBu_r",
            aspect="auto",
            text_auto=True
        )
    else:
        # Fallback to simple bar chart
        return build_simple_bar_chart(df, plan)
    
    return fig



