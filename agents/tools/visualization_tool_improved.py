import pandas as pd
import numpy as np
import json
import asyncio
from typing import Type, Dict, Any, List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class VisualizationInput(BaseModel):
    """Simplified input for DataFrame Visualization Tool."""
    dataframe_json: str = Field(..., description="JSON representation of the pandas DataFrame to visualize")
    chart_type: str = Field(..., description="Chart type: 'bar', 'line', 'pie', 'scatter', 'histogram'")
    title: str = Field(default="", description="Chart title (optional)")
    auto_select: bool = Field(default=True, description="Automatically select best columns for visualization")
    x_column: str = Field(default="", description="X-axis column (optional if auto_select=True)")
    y_column: str = Field(default="", description="Y-axis column (optional if auto_select=True)")


class VisualizationTool(BaseTool):
    """
    Simplified DataFrame Visualization Tool
    
    This tool automatically handles:
    - Column selection (finds best numeric/categorical columns)
    - Data aggregation (groups and sums automatically when needed)
    - Chart formatting (applies consistent styling)
    - Error handling (provides fallbacks)
    
    Agents only need to specify:
    1. dataframe_json: The data as JSON
    2. chart_type: What type of chart to create
    3. title: Optional chart title
    
    The tool does the rest automatically!
    """
    
    name: str = "Simplified DataFrame Visualization Tool"
    description: str = """
    Creates visualizations from pandas DataFrame data with minimal configuration.
    
    SIMPLE USAGE:
    - Provide data as JSON and specify chart type
    - Tool automatically selects best columns
    - Handles data preparation and formatting
    - Returns ready-to-use plot JSON specification
    
    SUPPORTED CHART TYPES:
    - 'bar': For categorical comparisons
    - 'line': For trends over time/sequence
    - 'pie': For part-to-whole relationships  
    - 'scatter': For correlation analysis
    - 'histogram': For distribution analysis
    """
    args_schema: Type[BaseModel] = VisualizationInput

    async def _run(self, dataframe_json: str, chart_type: str, title: str = "", 
                   auto_select: bool = True, x_column: str = "", y_column: str = "") -> str:
        """
        Creates visualizations with automatic column selection and formatting.
        
        Args:
            dataframe_json: JSON representation of pandas DataFrame
            chart_type: Type of chart ('bar', 'line', 'pie', 'scatter', 'histogram')
            title: Optional chart title
            auto_select: Whether to automatically select best columns
            x_column: Optional specific x column (overrides auto_select)
            y_column: Optional specific y column (overrides auto_select)
            
        Returns:
            JSON string with structured response including plot_type, plot_spec, etc.
        """
        try:
            # Parse DataFrame
            df_dict = json.loads(dataframe_json)
            df = pd.DataFrame(df_dict)
            
            if df.empty:
                return json.dumps({"error": "DataFrame is empty"})
            
            # Store original columns for info
            original_x = x_column
            original_y = y_column
            
            # Auto-select columns if not specified
            if auto_select or not x_column or not y_column:
                x_column, y_column = await self._auto_select_columns(df, chart_type)
            
            # Prepare data for the specific chart type
            plot_data = await self._prepare_data(df, chart_type, x_column, y_column)
            
            # Generate plot specification
            plot_spec = await self._create_plot_spec(plot_data, chart_type, x_column, y_column, title)
            
            # Generate insights based on the data and chart type
            insights = await self._generate_insights(df, chart_type, x_column, y_column, plot_data)
            
            # Create auto-selection info
            auto_selected_info = ""
            if auto_select or not original_x or not original_y:
                auto_selected_info = f"Auto-selected columns: x='{x_column}', y='{y_column if y_column else 'N/A'}'"
            
            # Return structured response compatible with VisualizationJSON
            response = {
                "plot_type": chart_type,  # Frontend expects this field name
                "title": title or plot_spec.get("layout", {}).get("title", ""),
                "plot_spec": json.dumps(plot_spec),  # Plot spec as JSON string
                "auto_selected_columns": auto_selected_info,
                "insights": insights
            }
            
            return json.dumps(response, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"Visualization error: {str(e)}"})

    async def _auto_select_columns(self, df: pd.DataFrame, chart_type: str) -> tuple[str, str]:
        """Automatically select the best columns for the given chart type."""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Chart-specific column selection logic
        if chart_type == "histogram":
            # Histogram only needs one numeric column
            x_col = numeric_cols[0] if numeric_cols else categorical_cols[0] if categorical_cols else df.columns[0]
            return x_col, ""
        
        elif chart_type == "pie":
            # Pie chart: categorical for labels, numeric for values
            x_col = categorical_cols[0] if categorical_cols else df.columns[0]
            y_col = numeric_cols[0] if numeric_cols else df.columns[1] if len(df.columns) > 1 else df.columns[0]
            return x_col, y_col
        
        elif chart_type == "line":
            # Line chart: prefer datetime/sequence for x, numeric for y
            if datetime_cols:
                x_col = datetime_cols[0]
            elif categorical_cols:
                x_col = categorical_cols[0]
            else:
                x_col = df.columns[0]
            
            y_col = numeric_cols[0] if numeric_cols else df.columns[1] if len(df.columns) > 1 else df.columns[0]
            return x_col, y_col
        
        elif chart_type == "scatter":
            # Scatter: two numeric columns
            if len(numeric_cols) >= 2:
                return numeric_cols[0], numeric_cols[1]
            elif len(numeric_cols) == 1:
                x_col = categorical_cols[0] if categorical_cols else df.columns[0]
                return x_col, numeric_cols[0]
            else:
                return df.columns[0], df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        else:  # bar chart (default)
            # Bar chart: categorical for x, numeric for y
            x_col = categorical_cols[0] if categorical_cols else df.columns[0]
            y_col = numeric_cols[0] if numeric_cols else df.columns[1] if len(df.columns) > 1 else df.columns[0]
            return x_col, y_col

    async def _prepare_data(self, df: pd.DataFrame, chart_type: str, x_column: str, y_column: str) -> Dict[str, Any]:
        """Prepare data based on chart type with automatic aggregation."""
        
        if chart_type == "histogram":
            # Histogram just needs the values
            return {"x": df[x_column].tolist()}
        
        elif chart_type == "pie":
            # Pie chart: group by category and sum values
            if x_column and y_column and x_column != y_column:
                grouped = df.groupby(x_column)[y_column].sum().reset_index()
                # Limit to top 10 categories for readability
                if len(grouped) > 10:
                    top_9 = grouped.nlargest(9, y_column)
                    others_sum = grouped.nsmallest(len(grouped) - 9, y_column)[y_column].sum()
                    others_row = pd.DataFrame({x_column: ['Others'], y_column: [others_sum]})
                    grouped = pd.concat([top_9, others_row], ignore_index=True)
                
                return {
                    "labels": grouped[x_column].tolist(),
                    "values": grouped[y_column].tolist()
                }
            else:
                # Fallback: use value counts
                value_counts = df[x_column].value_counts().head(10)
                return {
                    "labels": value_counts.index.tolist(),
                    "values": value_counts.values.tolist()
                }
        
        elif chart_type in ["bar", "line"]:
            # Bar/Line: group by x and aggregate y values
            if x_column and y_column and x_column != y_column:
                # Check if we have numeric data in y_column
                if pd.api.types.is_numeric_dtype(df[y_column]):
                    # Numeric y: group and sum
                    grouped = df.groupby(x_column)[y_column].sum().reset_index()
                else:
                    # Non-numeric y: count occurrences
                    grouped = df.groupby(x_column)[y_column].count().reset_index()
                
                return {
                    "x": grouped[x_column].tolist(),
                    "y": grouped[y_column].tolist()
                }
            else:
                # Fallback: use value counts (this creates counts, not original values!)
                # This is the source of the bug - we should avoid this fallback for bar charts
                # when we have both x and y columns
                if y_column and x_column != y_column:
                    # If we have both columns, use them directly
                    return {
                        "x": df[x_column].tolist(),
                        "y": df[y_column].tolist()
                    }
                else:
                    # Only use value counts when we actually want counts
                    value_counts = df[x_column].value_counts()
                    return {
                        "x": value_counts.index.tolist(),
                        "y": value_counts.values.tolist()
                    }
        
        else:  # scatter
            # Scatter: use raw values
            return {
                "x": df[x_column].tolist(),
                "y": df[y_column].tolist() if y_column else df[x_column].tolist()
            }

    async def _create_plot_spec(self, data: Dict[str, Any], chart_type: str, 
                               x_column: str, y_column: str, title: str) -> Dict[str, Any]:
        """Create the final plot specification with consistent formatting."""
        
        # Base layout configuration matching original tool format
        base_layout = {
            "plot_bgcolor": "white",
            "paper_bgcolor": "white",
            "font": {"color": "#2E2E2E", "family": "Arial, sans-serif"},
            "title_font": {"size": 16, "color": "#1f1f1f"},
            "colorway": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
        }
        
        if chart_type == "bar":
            return {
                "type": "bar",
                "data": data,
                "layout": {
                    **base_layout,
                    "title": title or f"{y_column} by {x_column}",
                    "xaxis": {"title": x_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                    "yaxis": {"title": y_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                    "showlegend": False,
                    "barmode": "group"
                },
                "config": {"responsive": True}
            }
        
        elif chart_type == "line":
            return {
                "type": "line", 
                "data": data,
                "layout": {
                    **base_layout,
                    "title": title or f"{y_column} over {x_column}",
                    "xaxis": {"title": x_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                    "yaxis": {"title": y_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                    "showlegend": False
                },
                "config": {"responsive": True}
            }
        
        elif chart_type == "pie":
            return {
                "type": "pie",
                "data": {
                    "labels": data["labels"],
                    "values": data["values"],
                    "hovertemplate": "Category: %{label}<br>Value: %{value}<br>Percentage: %{percent}<extra></extra>",
                    "textinfo": "label+percent",
                    "textposition": "auto",
                    "marker": {
                        "colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
                    }
                },
                "layout": {
                    **base_layout,
                    "title": title or f"Distribution of {y_column} by {x_column}",
                    "showlegend": True
                },
                "config": {"responsive": True}
            }
        
        elif chart_type == "scatter":
            return {
                "type": "scatter",
                "data": {
                    "x": data["x"],
                    "y": data["y"],
                    "mode": "markers"
                },
                "layout": {
                    **base_layout,
                    "title": title or f"{y_column} vs {x_column}",
                    "xaxis": {"title": x_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                    "yaxis": {"title": y_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                    "showlegend": False
                },
                "config": {"responsive": True}
            }
        
        elif chart_type == "histogram":
            return {
                "type": "histogram",
                "data": data,
                "layout": {
                    **base_layout,
                    "title": title or f"Distribution of {x_column}",
                    "xaxis": {"title": x_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                    "yaxis": {"title": "Frequency", "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                    "showlegend": False
                },
                "config": {"responsive": True}
            }
        
        else:
            # Return error for unsupported chart types
            raise ValueError(f"Unsupported chart type: {chart_type}. Supported types: bar, line, pie, scatter, histogram")

    async def _generate_insights(self, df: pd.DataFrame, chart_type: str, 
                                x_column: str, y_column: str, plot_data: Dict[str, Any]) -> str:
        """Generate insights based on the data and chart type."""
        try:
            insights = []
            
            if chart_type == "bar":
                if "x" in plot_data and "y" in plot_data:
                    max_value = max(plot_data["y"]) if plot_data["y"] else 0
                    max_idx = plot_data["y"].index(max_value) if plot_data["y"] else 0
                    max_category = plot_data["x"][max_idx] if max_idx < len(plot_data["x"]) else "Unknown"
                    insights.append(f"Highest value: {max_category} ({max_value})")
                    insights.append(f"Total categories: {len(plot_data['x'])}")
            
            elif chart_type == "pie":
                if "labels" in plot_data and "values" in plot_data:
                    total = sum(plot_data["values"]) if plot_data["values"] else 0
                    if total > 0 and plot_data["values"]:
                        max_value = max(plot_data["values"])
                        max_idx = plot_data["values"].index(max_value)
                        max_category = plot_data["labels"][max_idx] if max_idx < len(plot_data["labels"]) else "Unknown"
                        percentage = (max_value / total * 100) if total > 0 else 0
                        insights.append(f"Largest segment: {max_category} ({percentage:.1f}%)")
                        insights.append(f"Total segments: {len(plot_data['labels'])}")
            
            elif chart_type == "line":
                if "y" in plot_data and plot_data["y"]:
                    trend = "increasing" if plot_data["y"][-1] > plot_data["y"][0] else "decreasing"
                    insights.append(f"Overall trend: {trend}")
                    insights.append(f"Data points: {len(plot_data['y'])}")
            
            elif chart_type == "scatter":
                if "x" in plot_data and "y" in plot_data:
                    insights.append(f"Data points: {len(plot_data['x'])}")
                    insights.append(f"Scatter plot showing relationship between {x_column} and {y_column}")
            
            elif chart_type == "histogram":
                if "x" in plot_data:
                    insights.append(f"Distribution of {x_column}")
                    insights.append(f"Data points: {len(plot_data['x'])}")
            
            return "; ".join(insights) if insights else f"Visualization shows {chart_type} chart of the data"
            
        except Exception as e:
            return f"Generated {chart_type} chart successfully"


# Alias for backward compatibility
#DataFrameVisualizationToolImproved = SimplifiedVisualizationTool
