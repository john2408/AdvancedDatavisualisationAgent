
import pandas as pd
import numpy as np
import json
import os
from typing import Type, Dict, Any, List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import plotly.graph_objects as go
import plotly.express as px


class CSVVisualizationInput(BaseModel):
    """Input for CSV Visualization Tool."""
    file_path: str = Field(..., description="Path to the CSV file to visualize")
    plot_type: str = Field(..., description="Type of plot: 'histogram', 'scatter', 'boxplot', 'correlation_heatmap'")
    x_column: str = Field(default="", description="X-axis column name")
    y_column: str = Field(default="", description="Y-axis column name")
    title: str = Field(default="", description="Plot title")



class CSVVisualizationTool(BaseTool):
    name: str = "CSV Visualization Tool"
    description: str = "Creates visualizations from CSV data and saves them as HTML files."
    args_schema: Type[BaseModel] = CSVVisualizationInput

    def _run(self, file_path: str, plot_type: str, x_column: str = "", y_column: str = "", title: str = "") -> str:
        """
        Creates visualizations from CSV data.
        
        Args:
            file_path: Path to the CSV file
            plot_type: Type of plot to create
            x_column: X-axis column name
            y_column: Y-axis column name
            title: Plot title
            
        Returns:
            String with visualization creation status
        """
        try:
            if not os.path.exists(file_path):
                return f"Error: File '{file_path}' not found."
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Create output directory if it doesn't exist
            os.makedirs("output", exist_ok=True)
            
            fig = None
            
            if plot_type == "histogram":
                if not x_column or x_column not in df.columns:
                    return f"Error: Valid x_column required for histogram. Available columns: {list(df.columns)}"
                
                fig = px.histogram(df, x=x_column, title=title or f"Histogram of {x_column}")
                
            elif plot_type == "scatter":
                if not x_column or x_column not in df.columns:
                    return f"Error: Valid x_column required for scatter plot. Available columns: {list(df.columns)}"
                if not y_column or y_column not in df.columns:
                    return f"Error: Valid y_column required for scatter plot. Available columns: {list(df.columns)}"
                
                fig = px.scatter(df, x=x_column, y=y_column, title=title or f"Scatter plot: {x_column} vs {y_column}")
                
            elif plot_type == "boxplot":
                if not x_column or x_column not in df.columns:
                    return f"Error: Valid x_column required for boxplot. Available columns: {list(df.columns)}"
                
                fig = px.box(df, y=x_column, title=title or f"Boxplot of {x_column}")
                
            elif plot_type == "correlation_heatmap":
                numeric_df = df.select_dtypes(include=[np.number])
                if numeric_df.empty:
                    return "Error: No numeric columns found for correlation heatmap."
                
                corr_matrix = numeric_df.corr()
                fig = px.imshow(corr_matrix, 
                               text_auto=True,
                               aspect="auto",
                               title=title or "Correlation Heatmap")
                
            else:
                return f"Error: Unknown plot type '{plot_type}'. Available types: histogram, scatter, boxplot, correlation_heatmap"
            
            if fig:
                # Save as HTML
                output_file = f"output/csv_visualization_{plot_type}.html"
                fig.write_html(output_file)
                
                # Also save plot data as JSON for potential further processing
                plot_data = {
                    "plot_type": plot_type,
                    "x_column": x_column,
                    "y_column": y_column,
                    "title": title,
                    "data_shape": df.shape,
                    "file_path": file_path
                }
                
                with open("output/csv_visualization.json", "w") as f:
                    json.dump(plot_data, f, indent=2)
                
                return f"Visualization created successfully and saved as {output_file}"
            
        except Exception as e:
            return f"Error creating visualization: {str(e)}"
