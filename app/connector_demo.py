"""Streamlit demo app for testing connectors."""

import streamlit as st
import pandas as pd
from typing import Dict, Any
import json

from backend.db.postgres import get_postgres_connector
from backend.services.elasticsearch import get_elasticsearch_connector
from backend.services.web_search import get_web_search_connector

def display_query_result(result: Dict[str, Any]):
    """Display query results in a formatted way."""
    st.json(result)

def main():
    st.set_page_config(page_title="Connector Testing Demo", layout="wide")
    
    st.title("🔌 Connector Testing Dashboard")
    
    # Sidebar for selecting connector
    with st.sidebar:
        st.title("Test Configuration")
        connector_type = st.selectbox(
            "Select Connector to Test",
            ["PostgreSQL", "Elasticsearch", "Web Search"]
        )
        
        st.divider()
        
        # Test mode toggle
        is_test_mode = st.checkbox("Test Mode", value=True)
        if is_test_mode:
            st.info("Running in test mode - using mock data")
    
    # Main content area
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Test Input")
        
        if connector_type == "PostgreSQL":
            query = st.text_area(
                "SQL Query",
                value="SELECT * FROM sales LIMIT 5",
                height=100
            )
            
            if st.button("Execute Query"):
                with st.spinner("Executing query..."):
                    try:
                        db = get_postgres_connector()
                        results = db.execute_query(query)
                        with col2:
                            st.subheader("Query Results")
                            st.dataframe(pd.DataFrame(results))
                    except Exception as e:
                        st.error(f"Query failed: {str(e)}")
        
        elif connector_type == "Elasticsearch":
            search_type = st.radio("Search Type", ["Semantic", "Keyword"])
            
            if search_type == "Semantic":
                # For demo purposes, use a simple vector
                query_vector = [0.1, 0.2, 0.3, 0.4]
                k = st.slider("Number of results", 1, 10, 5)
                
                if st.button("Search"):
                    with st.spinner("Searching..."):
                        try:
                            es = get_elasticsearch_connector()
                            results = es.semantic_search(query_vector, k=k)
                            with col2:
                                st.subheader("Search Results")
                                for doc in results:
                                    st.write(doc)
                        except Exception as e:
                            st.error(f"Search failed: {str(e)}")
            else:
                query = st.text_input("Search Query", "test document")
                k = st.slider("Number of results", 1, 10, 5)
                
                if st.button("Search"):
                    with st.spinner("Searching..."):
                        try:
                            es = get_elasticsearch_connector()
                            results = es.keyword_search(query, k=k)
                            with col2:
                                st.subheader("Search Results")
                                for doc in results:
                                    st.write(doc)
                        except Exception as e:
                            st.error(f"Search failed: {str(e)}")
        
        else:  # Web Search
            query = st.text_input("Search Query", "latest market trends")
            include_answer = st.checkbox("Include AI Answer", value=True)
            
            if st.button("Search"):
                with st.spinner("Searching..."):
                    try:
                        web = get_web_search_connector()
                        if include_answer:
                            answer = web.get_answer(query)
                            with col2:
                                st.subheader("AI Answer")
                                st.write(answer)
                                st.divider()
                        
                        results = web.search(query)
                        with col2:
                            st.subheader("Search Results")
                            st.json(results)
                    except Exception as e:
                        st.error(f"Search failed: {str(e)}")
    
    # Display test information
    if is_test_mode:
        with st.expander("Test Information"):
            st.code("""
            Test Mode Configuration:
            - PostgreSQL: Returns mock data
            - Elasticsearch: Uses test index
            - Web Search: Returns cached responses
            """)

if __name__ == "__main__":
    main() 