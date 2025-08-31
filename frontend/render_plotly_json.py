import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Figure
from frontend.plotly_styles import apply_white_theme_styling

def render_plotly_from_json(plot_spec_json: str, df: pd.DataFrame) -> go.Figure | None:
    """Create a Plotly figure from JSON specification and DataFrame."""
    try:
        plot_spec = json.loads(plot_spec_json)
        
        fig = Figure(**plot_spec)
                
        # Apply white theme styling
        fig = apply_white_theme_styling(fig)
                
        return fig
        
    except json.JSONDecodeError as e:
        st.error(f"Error parsing plot JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating plot from JSON: {e}")
        return None


def _legacy_create_plotly_from_json(plot_spec_json: str, df: pd.DataFrame) -> go.Figure:
    """Create a Plotly figure from JSON specification and DataFrame."""
    try:
        plot_spec = json.loads(plot_spec_json)
        
        if "error" in plot_spec:
            st.error(f"Plot specification error: {plot_spec['error']}")
            return None
        
        plot_type = plot_spec.get("type")
        data = plot_spec.get("data", {})
        layout = plot_spec.get("layout", {})
        
        if not data:
            st.warning("No data found in plot specification")
            return None
        
        fig = None
        
        if plot_type == "bar":
            if "color" in data and data["color"]:
                # Grouped bar chart
                df_plot = pd.DataFrame({
                    "x": data["x"],
                    "y": data["y"],
                    "color": data["color"]
                })
                fig = px.bar(df_plot, x="x", y="y", color="color", title=layout.get("title"),
                           color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"])
            else:
                # Simple bar chart
                fig = px.bar(x=data.get("x", []), y=data.get("y", []), title=layout.get("title"),
                           color_discrete_sequence=["#1f77b4"])
                
        elif plot_type == "line":
            if "color" in data and data["color"]:
                df_plot = pd.DataFrame({
                    "x": data["x"],
                    "y": data["y"],
                    "color": data["color"]
                })
                fig = px.line(df_plot, x="x", y="y", color="color", title=layout.get("title"),
                            color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"])
            else:
                fig = px.line(x=data.get("x", []), y=data.get("y", []), title=layout.get("title"),
                            color_discrete_sequence=["#1f77b4"])
                
        elif plot_type == "scatter":
            if "color" in data and data["color"]:
                df_plot = pd.DataFrame({
                    "x": data["x"],
                    "y": data["y"],
                    "color": data["color"]
                })
                fig = px.scatter(df_plot, x="x", y="y", color="color", title=layout.get("title"),
                               color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"])
            else:
                fig = px.scatter(x=data.get("x", []), y=data.get("y", []), title=layout.get("title"),
                               color_discrete_sequence=["#1f77b4"])
                
        elif plot_type == "pie":
            if "values" in data and "labels" in data:
                fig = px.pie(values=data["values"], names=data["labels"], title=layout.get("title"),
                           color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"])
            
        elif plot_type == "histogram":
            if "x" in data:
                fig = px.histogram(x=data["x"], title=layout.get("title"),
                                 color_discrete_sequence=["#1f77b4"])
            
        elif plot_type == "box":
            if "y" in data:
                fig = px.box(y=data["y"], title=layout.get("title"),
                           color_discrete_sequence=["#1f77b4"])
            elif "x" in data:
                fig = px.box(y=data["x"], title=layout.get("title"),
                           color_discrete_sequence=["#1f77b4"])
                
        elif plot_type == "heatmap":
            if "z" in data and "x" in data and "y" in data:
                fig = px.imshow(
                    z=data["z"], 
                    x=data["x"], 
                    y=data["y"], 
                    title=layout.get("title"),
                    text_auto=True,
                    color_continuous_scale="RdBu_r"
                )
        
        if fig:
            # Apply any additional layout configurations from plot spec
            if layout.get("xaxis", {}).get("title"):
                fig.update_xaxes(title_text=layout["xaxis"]["title"])
            if layout.get("yaxis", {}).get("title"):
                fig.update_yaxes(title_text=layout["yaxis"]["title"])
                
            # Apply white theme styling
            fig = apply_white_theme_styling(fig)
                
            # Set responsive layout and height
            fig.update_layout(
                height=500,
                showlegend=layout.get("showlegend", True)
            )
                
        return fig
        
    except json.JSONDecodeError as e:
        st.error(f"Error parsing plot JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating plot from JSON: {e}")
        return None

