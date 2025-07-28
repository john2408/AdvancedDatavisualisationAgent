"""Tests for Elasticsearch connector."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.services.elasticsearch import ElasticsearchConnector
from elasticsearch import Elasticsearch

def test_elasticsearch_init(mock_elasticsearch_settings):
    """Test Elasticsearch connector initialization."""
    with patch('os.getenv', return_value="false"):
        with patch.object(Elasticsearch, '__init__', return_value=None) as mock_init:
            connector = ElasticsearchConnector(**mock_elasticsearch_settings)
            assert connector.host == mock_elasticsearch_settings['host']
            assert connector.index_name == mock_elasticsearch_settings['index_name']
            
            # Verify Elasticsearch client initialization
            mock_init.assert_called_once_with(
                hosts=[mock_elasticsearch_settings['host']],
                api_key=mock_elasticsearch_settings['api_key'],
                verify_certs=mock_elasticsearch_settings['verify_certs']
            )

def test_semantic_search(mock_elasticsearch_settings, sample_document):
    """Test semantic search functionality."""
    with patch('os.getenv', return_value="false"):
        # Create a mock Elasticsearch instance
        mock_es = MagicMock(spec=Elasticsearch)
        mock_es.search.return_value = {
            'hits': {
                'hits': [
                    {
                        '_source': sample_document,
                        '_score': 0.95
                    }
                ]
            }
        }
        
        with patch.object(Elasticsearch, '__init__', return_value=None):
            connector = ElasticsearchConnector(**mock_elasticsearch_settings)
            connector.client = mock_es
            
            # Perform search
            results = connector.semantic_search([0.1, 0.2, 0.3, 0.4])
            
            # Verify results
            assert len(results) == 1
            assert results[0]['content'] == sample_document['content']
            assert results[0]['score'] == 0.95
            
            # Verify search parameters
            mock_es.search.assert_called_once()
            call_args = mock_es.search.call_args[1]
            assert call_args['index'] == mock_elasticsearch_settings['index_name']
            assert 'script_score' in call_args['body']['query']

def test_keyword_search(mock_elasticsearch_settings, sample_document):
    """Test keyword-based search functionality."""
    with patch('os.getenv', return_value="false"):
        # Create a mock Elasticsearch instance
        mock_es = MagicMock(spec=Elasticsearch)
        mock_es.search.return_value = {
            'hits': {
                'hits': [
                    {
                        '_source': sample_document,
                        '_score': 0.85
                    }
                ]
            }
        }
        
        with patch.object(Elasticsearch, '__init__', return_value=None):
            connector = ElasticsearchConnector(**mock_elasticsearch_settings)
            connector.client = mock_es
            
            # Perform search
            results = connector.keyword_search("test document")
            
            # Verify results
            assert len(results) == 1
            assert results[0]['content'] == sample_document['content']
            assert results[0]['score'] == 0.85
            
            # Verify search parameters
            mock_es.search.assert_called_once()
            call_args = mock_es.search.call_args[1]
            assert call_args['index'] == mock_elasticsearch_settings['index_name']
            assert 'multi_match' in call_args['body']['query']

def test_search_error(mock_elasticsearch_settings):
    """Test error handling during search."""
    with patch('os.getenv', return_value="false"):
        # Create a mock Elasticsearch instance
        mock_es = MagicMock(spec=Elasticsearch)
        mock_es.search.side_effect = Exception("Search failed")
        
        with patch.object(Elasticsearch, '__init__', return_value=None):
            connector = ElasticsearchConnector(**mock_elasticsearch_settings)
            connector.client = mock_es
            
            with pytest.raises(Exception) as exc_info:
                connector.semantic_search([0.1, 0.2, 0.3, 0.4])
            
            assert "Search failed" in str(exc_info.value) 