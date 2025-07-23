"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, patch
import os
from typing import Dict, Any

# Set testing environment
os.environ["TESTING"] = "true"

@pytest.fixture
def mock_postgres_settings() -> Dict[str, Any]:
    """Mock PostgreSQL connection settings."""
    return {
        "host": "localhost",
        "database": "test_db",
        "user": "test_user",
        "password": "test_pass",  # Make sure this matches what's used in the factory
        "port": 5432
    }

@pytest.fixture
def mock_elasticsearch_settings() -> Dict[str, Any]:
    """Mock Elasticsearch connection settings."""
    return {
        "host": "http://localhost:9200",
        "api_key": "test_key",
        "index_name": "test_index",
        "verify_certs": False
    }

@pytest.fixture
def mock_web_search_settings() -> Dict[str, Any]:
    """Mock web search API settings."""
    return {
        "api_key": "test_tavily_key",
        "base_url": "https://api.tavily.com/v1"
    }

@pytest.fixture
def sample_document() -> Dict[str, Any]:
    """Sample document for testing."""
    return {
        "content": "This is a test document",
        "metadata": {
            "title": "Test Doc",
            "author": "Test Author"
        },
        "embedding": [0.1, 0.2, 0.3, 0.4]  # Mock embedding vector
    } 