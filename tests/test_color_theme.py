#!/usr/bin/env python3
"""
Test script to verify the new white theme color palette implementation.
"""

import sys
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.tools.visualization_tool import DataFrameVisualizationTool

def test_color_specifications():
    """Test that all chart types include proper color specifications."""
    
    print("🎨 Testing Color Theme Implementation")
    print("=" * 50)
    
    # Create sample data
    sample_data = pd.DataFrame({
        'category': ['BMW', 'Mercedes', 'Audi', 'Volkswagen', 'Toyota'],
        'value': [1200, 980, 850, 1100, 750],
        'region': ['Europe', 'Europe', 'Europe', 'Europe', 'Asia']
    })
    
    viz_tool = DataFrameVisualizationTool()
    dataframe_json = sample_data.to_json(orient='records')
    
    # Test different chart types
    chart_types = ['bar', 'line', 'scatter', 'pie', 'histogram', 'boxplot', 'heatmap']
    
    for chart_type in chart_types:
        print(f"\n📊 Testing {chart_type.upper()} chart...")
        
        try:
            result = viz_tool._run(
                dataframe_json=dataframe_json,
                plot_type=chart_type,
                x_column='category',
                y_column='value',
                color_column='region' if chart_type in ['bar', 'line', 'scatter'] else '',
                title=f'Test {chart_type.title()} Chart'
            )
            
            plot_spec = json.loads(result)
            
            if "error" in plot_spec:
                print(f"   ❌ Error: {plot_spec['error']}")
                continue
            
            # Check for white theme properties
            layout = plot_spec.get('layout', {})
            
            # Check background colors
            if 'plot_bgcolor' in layout and layout['plot_bgcolor'] == 'white':
                print("   ✅ Plot background: white")
            else:
                print("   ❌ Plot background: missing or not white")
            
            if 'paper_bgcolor' in layout and layout['paper_bgcolor'] == 'white':
                print("   ✅ Paper background: white")
            else:
                print("   ❌ Paper background: missing or not white")
            
            # Check font settings
            if 'font' in layout and 'color' in layout['font']:
                print(f"   ✅ Font color: {layout['font']['color']}")
            else:
                print("   ❌ Font color: missing")
            
            # Check color palette
            if 'colorway' in layout:
                colors = layout['colorway']
                print(f"   ✅ Color palette: {len(colors)} colors defined")
                print(f"      Primary colors: {colors[:3]}")
            elif chart_type == 'pie' and 'data' in plot_spec:
                pie_data = plot_spec['data']
                if 'marker' in pie_data and 'colors' in pie_data['marker']:
                    colors = pie_data['marker']['colors']
                    print(f"   ✅ Pie colors: {len(colors)} colors defined")
                    print(f"      Primary colors: {colors[:3]}")
                else:
                    print("   ❌ Pie colors: missing")
            else:
                print("   ❌ Color palette: missing")
            
            print(f"   📋 Layout keys: {list(layout.keys())}")
            
        except Exception as e:
            print(f"   ❌ Failed to create {chart_type} chart: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Color theme testing completed!")

def test_color_consistency():
    """Test that the professional color palette is consistent."""
    
    print("\n🎯 Testing Color Consistency")
    print("=" * 50)
    
    expected_colors = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
    ]
    
    # Create sample data
    sample_data = pd.DataFrame({
        'category': ['A', 'B', 'C', 'D', 'E'],
        'value': [100, 200, 150, 300, 250]
    })
    
    viz_tool = DataFrameVisualizationTool()
    dataframe_json = sample_data.to_json(orient='records')
    
    # Test bar chart colors
    result = viz_tool._run(
        dataframe_json=dataframe_json,
        plot_type='bar',
        x_column='category',
        y_column='value',
        title='Color Consistency Test'
    )
    
    plot_spec = json.loads(result)
    
    if "error" not in plot_spec:
        layout = plot_spec.get('layout', {})
        colorway = layout.get('colorway', [])
        
        print(f"Expected colors: {expected_colors[:5]}")
        print(f"Actual colors:   {colorway[:5]}")
        
        if colorway == expected_colors:
            print("✅ Color palette matches expected professional colors")
        else:
            print("❌ Color palette does not match expected colors")
            
        # Check specific color properties
        if colorway[0] == "#1f77b4":
            print("✅ Primary blue color correct")
        else:
            print(f"❌ Primary blue should be #1f77b4, got {colorway[0] if colorway else 'None'}")
    else:
        print(f"❌ Error testing color consistency: {plot_spec['error']}")

def test_white_theme_properties():
    """Test specific white theme properties."""
    
    print("\n🖼️  Testing White Theme Properties")
    print("=" * 50)
    
    # Create sample data
    sample_data = pd.DataFrame({
        'month': ['Jan', 'Feb', 'Mar', 'Apr'],
        'sales': [1000, 1200, 1100, 1300],
        'region': ['North', 'South', 'East', 'West']
    })
    
    viz_tool = DataFrameVisualizationTool()
    dataframe_json = sample_data.to_json(orient='records')
    
    # Test bar chart with color grouping
    result = viz_tool._run(
        dataframe_json=dataframe_json,
        plot_type='bar',
        x_column='month',
        y_column='sales',
        color_column='region',
        title='White Theme Test Chart'
    )
    
    plot_spec = json.loads(result)
    
    if "error" not in plot_spec:
        layout = plot_spec.get('layout', {})
        
        # Check all white theme properties
        white_theme_checks = [
            ('plot_bgcolor', 'white', 'Plot background'),
            ('paper_bgcolor', 'white', 'Paper background'),
        ]
        
        for prop, expected, description in white_theme_checks:
            if layout.get(prop) == expected:
                print(f"✅ {description}: {layout.get(prop)}")
            else:
                print(f"❌ {description}: expected '{expected}', got '{layout.get(prop)}'")
        
        # Check font properties
        font = layout.get('font', {})
        if font.get('color') == '#2E2E2E':
            print(f"✅ Font color: {font.get('color')}")
        else:
            print(f"❌ Font color: expected '#2E2E2E', got '{font.get('color')}'")
        
        if font.get('family') == 'Arial, sans-serif':
            print(f"✅ Font family: {font.get('family')}")
        else:
            print(f"❌ Font family: expected 'Arial, sans-serif', got '{font.get('family')}'")
        
        # Check title font
        title_font = layout.get('title_font', {})
        if title_font.get('color') == '#1f1f1f':
            print(f"✅ Title color: {title_font.get('color')}")
        else:
            print(f"❌ Title color: expected '#1f1f1f', got '{title_font.get('color')}'")
    
    else:
        print(f"❌ Error testing white theme: {plot_spec['error']}")

if __name__ == "__main__":
    try:
        test_color_specifications()
        test_color_consistency()
        test_white_theme_properties()
        
        print("\n🎉 All color theme tests completed!")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        sys.exit(1)
