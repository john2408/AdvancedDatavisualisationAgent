"""Tests for Streamlit backend integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
import pandas as pd
import numpy as np

from app.main import main
from backend.api import BackendAPI
from backend.db.postgres import PostgresConnector
from backend.services.elasticsearch import ElasticsearchConnector
from backend.services.web_search import WebSearchConnector

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components."""
    with patch('streamlit.sidebar') as mock_sidebar, \
         patch('streamlit.title') as mock_title, \
         patch('streamlit.text_area') as mock_text_area, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.spinner') as mock_spinner, \
         patch('streamlit.error') as mock_error:
        
        # Configure mock behavior
        mock_text_area.return_value = "Show me sales data for last 6 months"
        mock_button.return_value = True
        
        yield {
            'sidebar': mock_sidebar,
            'title': mock_title,
            'text_area': mock_text_area,
            'button': mock_button,
            'spinner': mock_spinner,
            'error': mock_error
        }

@pytest.fixture
def mock_backend_api():
    """Mock Backend API responses."""
    with patch('backend.api.BackendAPI') as mock_api:
        # Mock database query response
        mock_api.query_database.return_value = [
            {'date': '2024-01-01', 'sales': 1000},
            {'date': '2024-02-01', 'sales': 1200},
        ]
        
        # Mock semantic search response
        mock_api.semantic_search.return_value = [
            {'content': 'Sales report 2024', 'score': 0.95},
        ]
        
        # Mock web search response
        mock_api.web_search.return_value = {
            'results': [
                {'title': 'Market Analysis', 'content': 'Industry trends...'}
            ]
        }
        
        yield mock_api

def test_data_query_integration(mock_streamlit, mock_backend_api):
    """Test database query integration."""
    with patch('app.main.BackendAPI', return_value=mock_backend_api):
        # Simulate user input
        user_query = "Show me sales data for last 6 months"
        mock_streamlit['text_area'].return_value = user_query
        
        # Run the app
        main()
        
        # Verify backend API was called
        mock_backend_api.query_database.assert_called_once()
        
        # Verify results were displayed
        mock_streamlit['error'].assert_not_called()

def test_document_search_integration(mock_streamlit, mock_backend_api):
    """Test document search integration."""
    with patch('app.main.BackendAPI', return_value=mock_backend_api):
        # Simulate user input
        user_query = "Find documents about sales strategy"
        mock_streamlit['text_area'].return_value = user_query
        
        # Run the app
        main()
        
        # Verify backend API was called
        mock_backend_api.semantic_search.assert_called_once()
        
        # Verify results were displayed
        mock_streamlit['error'].assert_not_called()

def test_web_search_integration(mock_streamlit, mock_backend_api):
    """Test web search integration."""
    with patch('app.main.BackendAPI', return_value=mock_backend_api):
        # Simulate user input
        user_query = "What are current market trends?"
        mock_streamlit['text_area'].return_value = user_query
        
        # Run the app
        main()
        
        # Verify backend API was called
        mock_backend_api.web_search.assert_called_once()
        
        # Verify results were displayed
        mock_streamlit['error'].assert_not_called()

def test_error_handling(mock_streamlit, mock_backend_api):
    """Test error handling in backend integration."""
    with patch('app.main.BackendAPI', return_value=mock_backend_api):
        # Simulate backend error
        mock_backend_api.query_database.side_effect = Exception("Database error")
        
        # Simulate user input
        user_query = "Show me sales data"
        mock_streamlit['text_area'].return_value = user_query
        
        # Run the app
        main()
        
        # Verify error was displayed
        mock_streamlit['error'].assert_called_once()

def test_multiple_data_sources(mock_streamlit, mock_backend_api):
    """Test integration with multiple data sources."""
    with patch('app.main.BackendAPI', return_value=mock_backend_api):
        # Simulate user input requiring multiple sources
        user_query = "Compare our sales with market trends"
        mock_streamlit['text_area'].return_value = user_query
        
        # Run the app
        main()
        
        # Verify multiple backend calls
        mock_backend_api.query_database.assert_called_once()
        mock_backend_api.web_search.assert_called_once()
        
        # Verify results were displayed
        mock_streamlit['error'].assert_not_called()

def test_visualization_integration(mock_streamlit, mock_backend_api):
    """Test visualization of backend data."""
    with patch('app.main.BackendAPI', return_value=mock_backend_api):
        # Mock data for visualization
        mock_data = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=6, freq='M'),
            'sales': [1000, 1200, 1100, 1300, 1250, 1400]
        })
        mock_backend_api.query_database.return_value = mock_data.to_dict('records')
        
        # Simulate user input
        user_query = "Show sales trend visualization"
        mock_streamlit['text_area'].return_value = user_query
        
        # Run the app
        main()
        
        # Verify data was fetched and visualization was created
        mock_backend_api.query_database.assert_called_once()
        # Add assertions for visualization components once implemented 