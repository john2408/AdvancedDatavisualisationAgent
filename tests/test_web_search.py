"""Tests for web search connector."""

import pytest
from unittest.mock import Mock, patch
from backend.services.web_search import WebSearchConnector

def test_web_search_init(mock_web_search_settings):
    """Test web search connector initialization."""
    connector = WebSearchConnector(**mock_web_search_settings)
    assert connector.api_key == mock_web_search_settings['api_key']
    assert connector.base_url == mock_web_search_settings['base_url']
    assert "Bearer" in connector.headers['Authorization']

def test_search(mock_web_search_settings):
    """Test search functionality."""
    with patch('requests.post') as mock_post:
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {
                    'title': 'Test Result',
                    'url': 'https://test.com',
                    'content': 'Test content'
                }
            ],
            'answer': 'This is a direct answer'
        }
        mock_post.return_value = mock_response
        mock_response.raise_for_status = Mock()
        
        # Create connector and perform search
        connector = WebSearchConnector(**mock_web_search_settings)
        results = connector.search("test query")
        
        # Verify results
        assert 'results' in results
        assert len(results['results']) == 1
        assert results['answer'] == 'This is a direct answer'
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == f"{mock_web_search_settings['base_url']}/search"
        assert call_args[1]['headers']['Authorization'] == f"Bearer {mock_web_search_settings['api_key']}"

def test_get_answer(mock_web_search_settings):
    """Test get_answer functionality."""
    with patch('requests.post') as mock_post:
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'answer': 'This is a direct answer',
            'results': []
        }
        mock_post.return_value = mock_response
        mock_response.raise_for_status = Mock()
        
        # Create connector and get answer
        connector = WebSearchConnector(**mock_web_search_settings)
        answer = connector.get_answer("what is python?")
        
        # Verify result
        assert answer == 'This is a direct answer'
        
        # Verify API call parameters
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['include_answer'] is True
        assert call_args[1]['json']['max_results'] == 3

def test_search_error(mock_web_search_settings):
    """Test error handling during search."""
    with patch('requests.post') as mock_post:
        mock_post.side_effect = Exception("API request failed")
        
        connector = WebSearchConnector(**mock_web_search_settings)
        with pytest.raises(Exception) as exc_info:
            connector.search("test query")
        
        assert "API request failed" in str(exc_info.value) 