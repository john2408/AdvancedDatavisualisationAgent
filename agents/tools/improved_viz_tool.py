
import pandas as pd
import numpy as np
import json
import os
from typing import Type, Dict, Any, List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import plotly.graph_objects as go


class AdvVisualizationInput(BaseModel):
    """Input for DataFrame Visualization Tool."""
    dataframe_json: str = Field(..., description="JSON representation of the pandas DataFrame to visualize")
    plot_type: str = Field(..., description="Type of plot: 'bar', 'line', 'scatter', 'histogram', 'pie', 'heatmap', 'boxplot'")
    x_column: str = Field(default="", description="X-axis column name")
    y_column: str = Field(default="", description="Y-axis column name")
    color_column: str = Field(default="", description="Column to use for color grouping")
    title: str = Field(default="", description="Plot title")
    aggregation: str = Field(default="", description="Aggregation method for grouped data: sum, count, mean, max, min")



class AdvVisualizationTool(BaseTool):
    name: str = "DataFrame Visualization Tool"
    description: str = """Creates visualizations from pandas DataFrame data and returns JSON formatted plot specifications.
    
    IMPORTANT PARAMETER USAGE:
    - plot_type: The main chart type to create (required)
    - target_plot_type: Use ONLY when user requests converting from one chart type to another (e.g., 'convert to pie chart', 'change to bar chart')
    - transformation: Specify data transformations needed (e.g., 'normalize', 'to_pie', 'convert_chart_type')
    - current_chart_type: The existing chart type (for conversion context)
    
    EXAMPLES:
    - New visualization: plot_type="bar" (target_plot_type not needed)
    - Chart conversion: plot_type="bar", target_plot_type="pie", transformation="to_pie"
    - Normalization: transformation="normalize" (works with any chart type)
    """
    args_schema: Type[BaseModel] = AdvVisualizationInput

    def _run(self, dataframe_json: str, plot_type: str, x_column: str = "", y_column: str = "", 
             color_column: str = "", title: str = "", aggregation: str = "") -> str:
        """
        Creates visualizations from DataFrame data and returns JSON plot specification.
        
        Args:
            dataframe_json: JSON representation of pandas DataFrame
            plot_type: Type of plot to create
            x_column: X-axis column name
            y_column: Y-axis column name
            color_column: Column for color grouping
            title: Plot title
            aggregation: Aggregation method for grouped data
            transformation: Data transformation to apply
            current_chart_type: Current chart type for transformation context
            target_plot_type: Target chart type when converting from one chart type to another
            
        Returns:
            JSON string with plot specification
        """
        try:
            # Parse JSON back to DataFrame
            df_dict = json.loads(dataframe_json)
            df = pd.DataFrame(df_dict)
            
            if df.empty:
                return json.dumps({"error": "DataFrame is empty"})
                        
            # Generate plot specification based on target plot type
            plot_spec = self._generate_plot_spec(df, plot_type, x_column, y_column, color_column, title, aggregation)
            
            return json.dumps(plot_spec, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"Error creating visualization: {str(e)}"})

    def _generate_plot_spec(self, df: pd.DataFrame, plot_type: str, x_column: str, 
                           y_column: str, color_column: str, title: str, aggregation: str) -> Dict[str, Any]:
        """Generate plot specification dictionary."""
        
        # Get column information
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Auto-select columns if not provided
        if not x_column and categorical_columns:
            x_column = categorical_columns[0]
        if not y_column and numeric_columns:
            y_column = numeric_columns[0]
        
        # Prepare data based on plot type
        plot_data = self._prepare_plot_data(df, plot_type, x_column, y_column, color_column, aggregation)
        
        # Generate plot specification
        if plot_type == "bar":
            return self._create_bar_spec(plot_data, x_column, y_column, color_column, title)
        elif plot_type == "line":
            return self._create_line_spec(plot_data, x_column, y_column, color_column, title)
        elif plot_type == "scatter":
            return self._create_scatter_spec(plot_data, x_column, y_column, color_column, title)
        elif plot_type == "pie":
            return self._create_pie_spec(plot_data, x_column, y_column, title)
        elif plot_type == "histogram":
            return self._create_histogram_spec(plot_data, x_column, title)
        elif plot_type == "boxplot":
            return self._create_boxplot_spec(plot_data, x_column, y_column, title)
        elif plot_type == "heatmap":
            return self._create_heatmap_spec(plot_data, title)
        else:
            return {"error": f"Unknown plot type: {plot_type}"}

    def _prepare_plot_data(self, df: pd.DataFrame, plot_type: str, x_column: str, 
                          y_column: str, color_column: str, aggregation: str) -> Dict[str, Any]:
        """Prepare data for plotting based on plot type and aggregation."""
        
        if plot_type == "heatmap":
            # For heatmap, use correlation matrix of numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
            if not numeric_df.empty:
                corr_matrix = numeric_df.corr()
                return {
                    "z": corr_matrix.values.tolist(),
                    "x": corr_matrix.columns.tolist(),
                    "y": corr_matrix.index.tolist()
                }
            else:
                return {"error": "No numeric columns for heatmap"}
        
        elif plot_type in ["bar", "line"] and x_column and y_column:
            # Group and aggregate data
            if color_column and color_column in df.columns:
                # Check if aggregation is needed
                if aggregation and aggregation.strip():
                    grouped = df.groupby([x_column, color_column])[y_column].agg(aggregation).reset_index()
                else:
                    # Use data directly without aggregation
                    grouped = df[[x_column, y_column, color_column]]
                return {
                    "x": grouped[x_column].tolist(),
                    "y": grouped[y_column].tolist(),
                    "color": grouped[color_column].tolist()
                }
            else:
                # Check if aggregation is needed
                if aggregation and aggregation.strip():
                    grouped = df.groupby(x_column)[y_column].agg(aggregation).reset_index()
                else:
                    # Use data directly without aggregation
                    grouped = df[[x_column, y_column]]
                return {
                    "x": grouped[x_column].tolist(),
                    "y": grouped[y_column].tolist()
                }
        
        elif plot_type == "pie" and x_column and y_column:
            # Aggregate data for pie chart
            if aggregation and aggregation.strip():
                grouped = df.groupby(x_column)[y_column].agg(aggregation).reset_index()
            else:
                # Use data directly without aggregation
                grouped = df[[x_column, y_column]]
            return {
                "labels": grouped[x_column].tolist(),
                "values": grouped[y_column].tolist()
            }
        
        else:
            # For scatter, histogram, boxplot - use raw data
            result = {}
            if x_column and x_column in df.columns:
                result["x"] = df[x_column].tolist()
            if y_column and y_column in df.columns:
                result["y"] = df[y_column].tolist()
            if color_column and color_column in df.columns:
                result["color"] = df[color_column].tolist()
            return result

    def _create_bar_spec(self, data: Dict, x_column: str, y_column: str, color_column: str, title: str) -> Dict[str, Any]:
        """Create bar chart specification."""
        
        # Check if this is normalized data (values likely sum to 100 per group)
        is_normalized = False
        if "y" in data and color_column:
            # Check if values are in percentage range and sum to ~100 per x-group
            values = data.get("y", [])
            if values and all(0 <= v <= 100 for v in values if v is not None):
                is_normalized = True
        
        # Set appropriate y-axis title and range
        y_title = y_column
        y_axis_config = {
            "title": y_title, 
            "title_font": {"color": "#000000"}, 
            "tickfont": {"color": "#000000"}
        }
        
        if is_normalized and color_column:
            y_title = f"{y_column} (%)"
            y_axis_config = {
                "title": y_title,
                "title_font": {"color": "#000000"},
                "tickfont": {"color": "#000000"},
                "range": [0, 100],
                "ticksuffix": "%"
            }
        
        # Set appropriate chart mode for stacked bars
        bar_mode = "group"  # default
        if color_column and is_normalized:
            bar_mode = "stack"  # normalized stacked
        elif color_column:
            bar_mode = "stack"  # regular stacked
        
        return {
            "type": "bar",
            "data": data,
            "layout": {
                "title": title or f"{y_column} by {x_column}",
                "xaxis": {"title": x_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                "yaxis": y_axis_config,
                "barmode": bar_mode,
                "showlegend": bool(color_column),
                "plot_bgcolor": "white",
                "paper_bgcolor": "white",
                "font": {"color": "#2E2E2E", "family": "Arial, sans-serif"},
                "title_font": {"size": 16, "color": "#1f1f1f"},
                "colorway": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
            },
            "config": {"responsive": True}
        }

    def _create_line_spec(self, data: Dict, x_column: str, y_column: str, color_column: str, title: str) -> Dict[str, Any]:
        """Create line chart specification."""
        return {
            "type": "line",
            "data": data,
            "layout": {
                "title": title or f"{y_column} over {x_column}",
                "xaxis": {"title": x_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                "yaxis": {"title": y_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                "showlegend": bool(color_column),
                "plot_bgcolor": "white",
                "paper_bgcolor": "white",
                "font": {"color": "#2E2E2E", "family": "Arial, sans-serif"},
                "title_font": {"size": 16, "color": "#1f1f1f"},
                "colorway": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
            },
            "config": {"responsive": True}
        }

    def _create_scatter_spec(self, data: Dict, x_column: str, y_column: str, color_column: str, title: str) -> Dict[str, Any]:
        """Create scatter plot specification."""
        return {
            "type": "scatter",
            "data": data,
            "layout": {
                "title": title or f"{y_column} vs {x_column}",
                "xaxis": {"title": x_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                "yaxis": {"title": y_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                "showlegend": bool(color_column),
                "plot_bgcolor": "white",
                "paper_bgcolor": "white",
                "font": {"color": "#2E2E2E", "family": "Arial, sans-serif"},
                "title_font": {"size": 16, "color": "#1f1f1f"},
                "colorway": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
            },
            "config": {"responsive": True}
        }

    def _create_pie_spec(self, data: Dict, x_column: str, y_column: str, title: str) -> Dict[str, Any]:
        """Create pie chart specification."""
        # Check if we have percentage data from transformations
        percentage_col = f'{y_column}_percentage'
        
        # If we have percentage data, use it for better pie chart representation
        labels = data.get("labels", [])
        values = data.get("values", [])
        
        # Create hover text that shows both absolute values and percentages
        if percentage_col in str(data) or "percentage" in y_column.lower():
            hover_template = "Category: %{label}<br>Value: %{value}<br>Percentage: %{percent}<extra></extra>"
        else:
            hover_template = "Category: %{label}<br>Value: %{value}<br>Percentage: %{percent}<extra></extra>"
        
        return {
            "type": "pie",
            "data": {
                "labels": labels,
                "values": values,
                "hovertemplate": hover_template,
                "textinfo": "label+percent",
                "textposition": "auto",
                "marker": {
                    "colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
                }
            },
            "layout": {
                "title": title or f"Distribution of {y_column} by {x_column}",
                "showlegend": True,
                "font": {"size": 12, "color": "#2E2E2E", "family": "Arial, sans-serif"},
                "plot_bgcolor": "white",
                "paper_bgcolor": "white",
                "title_font": {"size": 16, "color": "#1f1f1f"}
            },
            "config": {"responsive": True}
        }

    def _create_histogram_spec(self, data: Dict, x_column: str, title: str) -> Dict[str, Any]:
        """Create histogram specification."""
        return {
            "type": "histogram",
            "data": data,
            "layout": {
                "title": title or f"Distribution of {x_column}",
                "xaxis": {"title": x_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                "yaxis": {"title": "Frequency", "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                "plot_bgcolor": "white",
                "paper_bgcolor": "white",
                "font": {"color": "#2E2E2E", "family": "Arial, sans-serif"},
                "title_font": {"size": 16, "color": "#1f1f1f"},
                "colorway": ["#1f77b4"]
            },
            "config": {"responsive": True}
        }

    def _create_boxplot_spec(self, data: Dict, x_column: str, y_column: str, title: str) -> Dict[str, Any]:
        """Create boxplot specification."""
        return {
            "type": "box",
            "data": data,
            "layout": {
                "title": title or f"Distribution of {y_column or x_column}",
                "yaxis": {"title": y_column or x_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                "xaxis": {"title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
                "plot_bgcolor": "white",
                "paper_bgcolor": "white",
                "font": {"color": "#2E2E2E", "family": "Arial, sans-serif"},
                "title_font": {"size": 16, "color": "#1f1f1f"},
                "colorway": ["#1f77b4"]
            },
            "config": {"responsive": True}
        }

    def _create_heatmap_spec(self, data: Dict, title: str) -> Dict[str, Any]:
        """Create heatmap specification."""
        return {
            "type": "heatmap",
            "data": data,
            "layout": {
                "title": title or "Correlation Heatmap",
                "plot_bgcolor": "white",
                "paper_bgcolor": "white",
                "font": {"color": "#2E2E2E", "family": "Arial, sans-serif"},
                "title_font": {"size": 16, "color": "#1f1f1f"}
            },
            "config": {"responsive": True}
        }