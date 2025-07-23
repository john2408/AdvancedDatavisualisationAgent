"""Main Streamlit application for the Advanced Data Visualization Agent."""

import streamlit as st
import plotly.express as px
import pandas as pd
from typing import Optional

# Page configuration
st.set_page_config(
    page_title="AI Data Visualization Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTextInput > div > div > input {
        caret-color: #FF4B4B;
    }
    .stButton > button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    # Sidebar
    with st.sidebar:
        st.title("🤖 AI Data Assistant")
        st.markdown("---")
        
        # Input Method Selection
        input_method = st.radio(
            "Choose Input Method:",
            ["Text", "Voice"],
            index=0
        )
        
        # Data Source Selection
        data_source = st.multiselect(
            "Data Sources:",
            ["Internal Database", "Documents", "Web Data"],
            default=["Internal Database"]
        )
        
        st.markdown("---")
        st.markdown("### Model Settings")
        model = st.selectbox(
            "Language Model:",
            ["GPT-4", "GPT-3.5", "Claude"]
        )
    
    # Main Content
    st.title("Advanced Data Visualization Agent")
    
    # Input Area
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_area(
            "Ask me anything about your data...",
            placeholder="e.g., Show me sales trends for the last 6 months",
            height=100
        )
    with col2:
        st.write("")
        st.write("")
        analyze_button = st.button("Analyze 🔍", type="primary", use_container_width=True)
        
    # Results Area
    if analyze_button and user_input:
        with st.spinner("Processing your request..."):
            # Mock tabs for different views
            tab1, tab2, tab3 = st.tabs(["Visualization", "Analysis", "Data"])
            
            with tab1:
                st.markdown("### Sales Trend Analysis")
                # Mock data for demonstration
                df = pd.DataFrame({
                    'Month': pd.date_range(start='2023-01-01', periods=6, freq='M'),
                    'Sales': [12000, 15000, 18000, 16000, 19000, 22000]
                })
                fig = px.line(df, x='Month', y='Sales', 
                            title='Monthly Sales Trend',
                            template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.markdown("### Key Insights")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Average Monthly Sales", "$17,000", "+15%")
                with col2:
                    st.metric("Growth Rate", "83%", "↗️")
                
                st.markdown("""
                    #### Analysis Summary
                    - Sales show a consistent upward trend
                    - Highest growth observed in the last month
                    - Seasonal pattern detected in Q2
                """)
            
            with tab3:
                st.dataframe(df, use_container_width=True)
                
            # Sources and References
            st.markdown("---")
            st.markdown("### Sources")
            st.markdown("""
                - Internal Sales Database
                - Market Analysis Reports
                - Industry Benchmarks
            """)

if __name__ == "__main__":
    main() 