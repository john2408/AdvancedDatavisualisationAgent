# --- Built-in libraries ---
import json
import os

# --- Third-party libraries ---
# These must be listed in requirements.txt:
import pandas as pd
import numpy as np

# =====================================================================================
# --- Visualization Logic ---
# =====================================================================================

def _prepare_plot_data(df: pd.DataFrame, plot_type: str, x_column: str,
                      y_column: str, color_column: str, aggregation: str) -> dict:
    """Prepares data for plotting based on chart type and aggregation."""
    if plot_type == "heatmap":
        numeric_df = df.select_dtypes(include=[np.number])
        if not numeric_df.empty:
            corr_matrix = numeric_df.corr()
            return {"z": corr_matrix.values.tolist(), "x": corr_matrix.columns.tolist(), "y": corr_matrix.index.tolist()}
        else:
            return {"error": "No numeric columns found for heatmap"}
    
    grouping_cols = [x_column]
    if color_column and color_column in df.columns:
        grouping_cols.append(color_column)
    
    # Filter out empty grouping columns
    grouping_cols = [col for col in grouping_cols if col]

    if plot_type in ["bar", "line", "pie"] and x_column and y_column and aggregation:
        try:
            grouped = df.groupby(grouping_cols)[y_column].agg(aggregation).reset_index()
            return grouped.to_dict(orient='list')
        except Exception as e:
            return {"error": f"Error during aggregation: {e}"}
    else:
        # For scatter, histogram, boxplot, or when no aggregation is needed
        cols_to_return = [c for c in [x_column, y_column, color_column] if c and c in df.columns]
        if not cols_to_return:
            return {"error": "No valid columns found for visualization."}
        return df[cols_to_return].to_dict(orient='list')


def _create_bar_spec(data: dict, x_column: str, y_column: str, color_column: str, title: str) -> dict:
    """Creates the specification for a bar chart."""
    return {
        "type": "bar", "data": data,
        "layout": {
            "title": title or f"{y_column} by {x_column}",
            "xaxis": {"title": x_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
            "yaxis": {"title": y_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
            "barmode": "group" if color_column else "relative",
            "showlegend": bool(color_column),
            "plot_bgcolor": "white",
            "paper_bgcolor": "white",
            "font": {"color": "#2E2E2E", "family": "Arial, sans-serif"},
            "title_font": {"size": 16, "color": "#1f1f1f"},
            "colorway": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
        },
        "config": {"responsive": True}
    }

def _create_line_spec(data: dict, x_column: str, y_column: str, color_column: str, title: str) -> dict:
    """Creates the specification for a line chart."""
    return {
        "type": "line", "data": data,
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

def _create_scatter_spec(data: dict, x_column: str, y_column: str, color_column: str, title: str) -> dict:
    """Creates the specification for a scatter plot."""
    return {
        "type": "scatter", "data": data,
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

def _create_pie_spec(data: dict, x_column: str, y_column: str, title: str) -> dict:
    """Creates the specification for a pie chart."""
    # Create a new dictionary for pie data to avoid modifying the original
    pie_data = {
        'labels': data.get(x_column),
        'values': data.get(y_column),
        "textinfo": "label+percent",
        "textposition": "auto"
    }
    return {
        "type": "pie", "data": pie_data,
        "layout": {
            "title": title or f"Distribution of {y_column} by {x_column}",
            "showlegend": True,
            "font": {"size": 12, "color": "#2E2E2E", "family": "Arial, sans-serif"},
            "plot_bgcolor": "white",
            "paper_bgcolor": "white",
            "title_font": {"size": 16, "color": "#1f1f1f"},
            "colorway": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
        },
        "config": {"responsive": True}
    }

def _create_histogram_spec(data: dict, x_column: str, title: str) -> dict:
    """Creates the specification for a histogram."""
    return {
        "type": "histogram", "data": data,
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

def _create_boxplot_spec(data: dict, x_column: str, y_column: str, title: str) -> dict:
    """Creates the specification for a boxplot."""
    return {
        "type": "box", "data": data,
        "layout": {
            "title": title or f"Distribution of {y_column or x_column}",
            "yaxis": {"title": y_column or x_column, "title_font": {"color": "#000000"}, "tickfont": {"color": "#000000"}},
            "plot_bgcolor": "white",
            "paper_bgcolor": "white",
            "font": {"color": "#2E2E2E", "family": "Arial, sans-serif"},
            "title_font": {"size": 16, "color": "#1f1f1f"},
            "colorway": ["#1f77b4"]
        },
        "config": {"responsive": True}
    }

def _create_heatmap_spec(data: dict, title: str) -> dict:
    """Creates the specification for a heatmap."""
    return {
        "type": "heatmap", "data": data,
        "layout": {
            "title": title or "Correlation Heatmap",
            "plot_bgcolor": "white",
            "paper_bgcolor": "white",
            "font": {"color": "#2E2E2E", "family": "Arial, sans-serif"},
            "title_font": {"size": 16, "color": "#1f1f1f"}
        },
        "config": {"responsive": True}
    }

def _generate_plot_spec(df: pd.DataFrame, plot_type: str, x_column: str,
                       y_column: str, color_column: str, title: str, aggregation: str) -> dict:
    """Generates the complete plot specification."""
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Auto-select columns if not provided
    if not x_column and categorical_columns:
        x_column = categorical_columns[0]
    if not y_column and numeric_columns:
        y_column = numeric_columns[0]
    
    plot_data = _prepare_plot_data(df, plot_type, x_column, y_column, color_column, aggregation)
    
    if plot_data.get("error"):
        return plot_data

    specs = {
        "bar": _create_bar_spec, "line": _create_line_spec, "scatter": _create_scatter_spec,
        "pie": _create_pie_spec, "histogram": _create_histogram_spec, "boxplot": _create_boxplot_spec,
        "heatmap": _create_heatmap_spec
    }
    
    if plot_type in specs:
        if plot_type == "pie":
             return specs[plot_type](plot_data, x_column, y_column, title)
        elif plot_type == "histogram":
            return specs[plot_type](plot_data, x_column, title)
        elif plot_type == "boxplot":
            return specs[plot_type](plot_data, x_column, y_column, title)
        elif plot_type == "heatmap":
            return specs[plot_type](plot_data, title)
        return specs[plot_type](plot_data, x_column, y_column, color_column, title) # bar, line, scatter
    else:
        return {"error": f"Unknown chart type: {plot_type}"}

# =====================================================================================
# --- Main Function (Entry Point for Cloud Function) ---
# =====================================================================================
def main(params):
    """
    Main function called by IBM Cloud Functions.
    Takes a DataFrame and plot parameters and returns a Plotly JSON specification.
    """
    try:
        dataframe_json = params.get("dataframe_json")
        plot_type = params.get("plot_type")
        
        if not dataframe_json or not plot_type:
            raise ValueError("The 'dataframe_json' and 'plot_type' parameters are required.")
            
        # Load DataFrame from JSON string (in 'split' format)
        df = pd.read_json(dataframe_json, orient='split')

        # Generate plot specification
        plot_spec = _generate_plot_spec(
            df=df,
            plot_type=plot_type,
            x_column=params.get("x_column", ""),
            y_column=params.get("y_column", ""),
            color_column=params.get("color_column", ""),
            title=params.get("title", "Automatically Generated Chart"),
            aggregation=params.get("aggregation", "sum") # Set default aggregation to 'sum'
        )
        
        if plot_spec.get("error"):
             raise ValueError(plot_spec.get("error"))

        # Return successful response
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"plot_spec": plot_spec})
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        error_body = json.dumps({"error": str(e)})
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': error_body
        }
