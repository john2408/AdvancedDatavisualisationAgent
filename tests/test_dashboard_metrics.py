#!/usr/bin/env python3
"""
Test script to validate dashboard-style metrics formatting
"""

import streamlit as st
import pandas as pd

def display_dashboard_metric(title: str, value: str, col_obj):
    """Display a dashboard-style metric box with white background and black text."""
    with col_obj:
        st.markdown(f"""
        <div style="background-color: white; border: 1px solid #e1e5e9; border-radius: 0.25rem; padding: 1rem; margin: 0.25rem 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center;">
            <h3 style="margin: 0; color: #1F2937; font-size: 1.5rem; font-weight: 600;">{value}</h3>
            <p style="margin: 0.25rem 0 0 0; color: #6B7280; font-size: 0.875rem; font-weight: 500;">{title}</p>
        </div>
        """, unsafe_allow_html=True)

def test_dashboard_metrics():
    """Test the dashboard metrics display"""
    
    # Create test data
    test_df = pd.DataFrame({
        'Vehicle_Type': ['Car', 'Truck', 'Motorcycle', 'Electric Car', 'Hybrid'],
        'Count': [1500, 800, 300, 450, 250],
        'Registration_Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May']
    })
    
    st.title("🧪 Dashboard Metrics Test")
    st.write("Testing the new dashboard-style metrics boxes:")
    
    # Test metrics display
    col1, col2, col3 = st.columns(3)
    display_dashboard_metric("Total Rows", f"{len(test_df):,}", col1)
    display_dashboard_metric("Columns", str(len(test_df.columns)), col2)
    
    # Test numeric column logic
    numeric_cols = test_df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        numeric_col = numeric_cols[0]
        total_value = test_df[numeric_col].sum()
        display_dashboard_metric(f"Total {numeric_col}", f"{total_value:,.0f}", col3)
    else:
        display_dashboard_metric("Data Type", "Text/Mixed", col3)
    
    st.write("---")
    st.subheader("📊 Test Data")
    st.dataframe(test_df, use_container_width=True)
    
    st.success("✅ Dashboard metrics test completed!")
    st.info("💡 The metrics now have white backgrounds with borders, matching the SQL code styling!")

if __name__ == "__main__":
    test_dashboard_metrics()
