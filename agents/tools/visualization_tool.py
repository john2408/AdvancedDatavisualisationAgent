
import pandas as pd
import numpy as np
import json
import os
from typing import Type, Dict, Any, List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import plotly.graph_objects as go


class VisualizationInput(BaseModel):
    """Input for DataFrame Visualization Tool."""
    dataframe_json: str = Field(..., description="JSON representation of the pandas DataFrame to visualize")
    plot_type: str = Field(..., description="Type of plot: 'bar', 'line', 'scatter', 'histogram', 'pie', 'heatmap', 'boxplot'")
    x_column: str = Field(default="", description="X-axis column name")
    y_column: str = Field(default="", description="Y-axis column name")
    color_column: str = Field(default="", description="Column to use for color grouping")
    title: str = Field(default="", description="Plot title")
    aggregation: str = Field(default="sum", description="Aggregation method for grouped data: sum, count, mean, max, min")
    transformation: str = Field(default="", description="Data transformation: 'percentage', 'normalize', 'top_n', 'group_others'")
    current_chart_type: str = Field(default="", description="Current chart type for transformation context")



class DataFrameVisualizationTool(BaseTool):
    name: str = "DataFrame Visualization Tool"
    description: str = "Creates visualizations from pandas DataFrame data and returns JSON formatted plot specifications."
    args_schema: Type[BaseModel] = VisualizationInput

    def _run(self, dataframe_json: str, plot_type: str, x_column: str = "", y_column: str = "", 
             color_column: str = "", title: str = "", aggregation: str = "sum", 
             transformation: str = "", current_chart_type: str = "") -> str:
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
            
        Returns:
            JSON string with plot specification
        """
        try:
            # Parse JSON back to DataFrame
            df_dict = json.loads(dataframe_json)
            df = pd.DataFrame(df_dict)
            
            if df.empty:
                return json.dumps({"error": "DataFrame is empty"})
            
            # Apply intelligent transformations based on chart type conversion
            df_transformed = self._apply_intelligent_transformations(
                df, plot_type, current_chart_type, x_column, y_column, transformation
            )
            
            # Generate plot specification based on plot type
            plot_spec = self._generate_plot_spec(df_transformed, plot_type, x_column, y_column, 
                                                color_column, title, aggregation)
            
            return json.dumps(plot_spec, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"Error creating visualization: {str(e)}"})

    def _apply_intelligent_transformations(self, df: pd.DataFrame, target_plot_type: str, 
                                         current_plot_type: str, x_column: str, y_column: str, 
                                         transformation: str) -> pd.DataFrame:
        """Apply intelligent data transformations based on chart type conversion."""
        df_transformed = df.copy()
        
        try:
            # Scenario 1: Bar chart to Pie chart - Convert to percentages
            if current_plot_type == "bar" and target_plot_type == "pie":
                if x_column and y_column:
                    # Group by category and sum values
                    grouped = df_transformed.groupby(x_column)[y_column].sum().reset_index()
                    # Calculate percentages
                    total = grouped[y_column].sum()
                    grouped[f'{y_column}_percentage'] = (grouped[y_column] / total * 100).round(2)
                    grouped = grouped.sort_values(f'{y_column}_percentage', ascending=False)
                    
                    # Limit to top 8 categories, group rest as "Others"
                    if len(grouped) > 8:
                        top_categories = grouped.head(7)
                        others_sum = grouped.tail(len(grouped) - 7)[f'{y_column}_percentage'].sum()
                        others_row = pd.DataFrame({
                            x_column: ['Others'],
                            y_column: [grouped.tail(len(grouped) - 7)[y_column].sum()],
                            f'{y_column}_percentage': [others_sum]
                        })
                        grouped = pd.concat([top_categories, others_row], ignore_index=True)
                    
                    return grouped
            
            # Scenario 2: Any chart to Pie - Automatic percentage conversion
            elif target_plot_type == "pie" and x_column and y_column:
                # Group by category and sum values
                grouped = df_transformed.groupby(x_column)[y_column].sum().reset_index()
                # Calculate percentages
                total = grouped[y_column].sum()
                grouped[f'{y_column}_percentage'] = (grouped[y_column] / total * 100).round(2)
                grouped = grouped.sort_values(f'{y_column}_percentage', ascending=False)
                
                # Limit to top categories for better readability
                if len(grouped) > 10:
                    top_categories = grouped.head(9)
                    others_sum = grouped.tail(len(grouped) - 9)[f'{y_column}_percentage'].sum()
                    others_row = pd.DataFrame({
                        x_column: ['Others'],
                        y_column: [grouped.tail(len(grouped) - 9)[y_column].sum()],
                        f'{y_column}_percentage': [others_sum]
                    })
                    grouped = pd.concat([top_categories, others_row], ignore_index=True)
                
                return grouped
            
            # Scenario 3: Line to Bar - Aggregate time series appropriately
            elif current_plot_type == "line" and target_plot_type == "bar":
                if x_column and y_column:
                    # If x_column is time-like, aggregate by larger time periods
                    if df_transformed[x_column].dtype in ['datetime64[ns]', 'object']:
                        try:
                            df_transformed[x_column] = pd.to_datetime(df_transformed[x_column])
                            # Group by month or quarter for better bar chart representation
                            df_transformed['period'] = df_transformed[x_column].dt.to_period('M')
                            grouped = df_transformed.groupby('period')[y_column].sum().reset_index()
                            grouped['period'] = grouped['period'].astype(str)
                            grouped.rename(columns={'period': x_column}, inplace=True)
                            return grouped
                        except:
                            pass
            
            # Scenario 4: Explicit percentage transformation
            elif transformation == "percentage" and y_column:
                if x_column:
                    grouped = df_transformed.groupby(x_column)[y_column].sum().reset_index()
                    total = grouped[y_column].sum()
                    grouped[f'{y_column}_percentage'] = (grouped[y_column] / total * 100).round(2)
                    return grouped
            
            # Scenario 5: Top N transformation with Others grouping
            elif transformation.startswith("top_") and x_column and y_column:
                try:
                    n = int(transformation.split("_")[1])
                    grouped = df_transformed.groupby(x_column)[y_column].sum().reset_index()
                    grouped = grouped.sort_values(y_column, ascending=False)
                    
                    if len(grouped) > n:
                        top_n = grouped.head(n-1)
                        others_sum = grouped.tail(len(grouped) - (n-1))[y_column].sum()
                        others_row = pd.DataFrame({
                            x_column: ['Others'],
                            y_column: [others_sum]
                        })
                        grouped = pd.concat([top_n, others_row], ignore_index=True)
                    
                    return grouped
                except:
                    pass
            
            return df_transformed
            
        except Exception as e:
            # If transformation fails, return original data
            return df

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
        return {
            "type": "bar",
            "data": data,
            "layout": {
                "title": title or f"{y_column} by {x_column}",
                "xaxis": {"title": x_column},
                "yaxis": {"title": y_column},
                "showlegend": bool(color_column)
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
                "xaxis": {"title": x_column},
                "yaxis": {"title": y_column},
                "showlegend": bool(color_column)
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
                "xaxis": {"title": x_column},
                "yaxis": {"title": y_column},
                "showlegend": bool(color_column)
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
                "textposition": "auto"
            },
            "layout": {
                "title": title or f"Distribution of {y_column} by {x_column}",
                "showlegend": True,
                "font": {"size": 12}
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
                "xaxis": {"title": x_column},
                "yaxis": {"title": "Frequency"}
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
                "yaxis": {"title": y_column or x_column}
            },
            "config": {"responsive": True}
        }

    def _create_heatmap_spec(self, data: Dict, title: str) -> Dict[str, Any]:
        """Create heatmap specification."""
        return {
            "type": "heatmap",
            "data": data,
            "layout": {
                "title": title or "Correlation Heatmap"
            },
            "config": {"responsive": True}
        }
