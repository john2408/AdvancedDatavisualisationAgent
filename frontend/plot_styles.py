from plotly import graph_objects as go

def apply_white_theme_styling(fig: go.Figure) -> go.Figure:
    """Apply consistent white theme styling to all charts."""
    # Professional color palette optimized for white backgrounds
    professional_colors = [
        "#1f77b4",  # Blue
        "#ff7f0e",  # Orange
        "#2ca02c",  # Green
        "#d62728",  # Red
        "#9467bd",  # Purple
        "#8c564b",  # Brown
        "#e377c2",  # Pink
        "#7f7f7f",  # Gray
        "#bcbd22",  # Olive
        "#17becf"   # Cyan
    ]
    
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="#2E2E2E"
        ),
        title_font=dict(
            size=16,
            color="#1f1f1f"
        ),
        colorway=professional_colors,
        # Grid styling for better readability
        xaxis=dict(
            gridcolor="#E5E5E5",
            gridwidth=0.5,
            showgrid=True,
            zeroline=False,
            title_font=dict(color="#000000"),
            tickfont=dict(color="#000000")
        ),
        yaxis=dict(
            gridcolor="#E5E5E5",
            gridwidth=0.5,
            showgrid=True,
            zeroline=False,
            title_font=dict(color="#000000"),
            tickfont=dict(color="#000000")
        ),
        # Legend styling
        legend=dict(
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#E5E5E5",
            borderwidth=1,
            font=dict(color="#2E2E2E")
        )
    )
    
    # Update trace colors for consistent theming
    for i, trace in enumerate(fig.data):
        if hasattr(trace, 'marker'):
            if trace.type == 'bar':
                trace.marker.color = professional_colors[i % len(professional_colors)]
                trace.marker.line = dict(color="#FFFFFF", width=0.5)
            elif trace.type == 'scatter':
                trace.marker.color = professional_colors[i % len(professional_colors)]
                trace.marker.size = 8
                trace.marker.line = dict(color="white", width=1)
            elif trace.type == 'box':
                trace.marker.color = professional_colors[i % len(professional_colors)]
                trace.line.color = professional_colors[i % len(professional_colors)]
        
        if hasattr(trace, 'line') and trace.type in ['scatter', 'line']:
            trace.line.color = professional_colors[i % len(professional_colors)]
            trace.line.width = 3
    
    # Ensure all axis text is black for optimal readability
    fig.update_xaxes(
        title_font_color="#000000",
        tickfont_color="#000000"
    )
    fig.update_yaxes(
        title_font_color="#000000", 
        tickfont_color="#000000"
    )
    
    return fig