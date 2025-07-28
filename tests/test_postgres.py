"""Tests for PostgreSQL connector."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.db.postgres import PostgresConnector, get_postgres_connector
import psycopg2
import os

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment."""
    os.environ["TESTING"] = "true"
    yield
    os.environ.pop("TESTING", None)

@patch('psycopg2.connect')
def test_postgres_init(mock_connect, mock_postgres_settings):
    """Test PostgreSQL connector initialization."""
    connector = PostgresConnector(**mock_postgres_settings)
    assert connector.conn_params['host'] == mock_postgres_settings['host']
    assert connector.conn_params['database'] == mock_postgres_settings['database']
    assert connector.pool is None
    assert connector.conn is None

@patch('psycopg2.connect')
def test_execute_query(mock_connect, mock_postgres_settings):
    """Test query execution."""
    # Setup mock connection and cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {'id': 1, 'name': 'Test'},
        {'id': 2, 'name': 'Test2'}
    ]
    
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    
    # Create connector and execute query
    connector = PostgresConnector(**mock_postgres_settings)
    results = connector.execute_query("SELECT * FROM test")
    
    # Verify results
    assert len(results) == 2
    assert results[0]['name'] == 'Test'
    assert results[1]['id'] == 2
    
    # Verify correct method calls
    mock_cursor.execute.assert_any_call("SET TRANSACTION READ ONLY")
    mock_cursor.execute.assert_any_call("SELECT * FROM test", None)

@patch('psycopg2.connect')
def test_connection_error(mock_connect, mock_postgres_settings):
    """Test error handling during connection."""
    mock_connect.side_effect = psycopg2.OperationalError("Connection failed")
    
    connector = PostgresConnector(**mock_postgres_settings)
    with pytest.raises(psycopg2.OperationalError) as exc_info:
        connector.execute_query("SELECT * FROM test")
    
    assert "Connection failed" in str(exc_info.value)

@patch('psycopg2.connect')
def test_query_error(mock_connect, mock_postgres_settings):
    """Test error handling during query execution."""
    # Setup mock connection and cursor
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("Query failed")
    
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    
    connector = PostgresConnector(**mock_postgres_settings)
    with pytest.raises(Exception) as exc_info:
        connector.execute_query("SELECT * FROM test")
    
    assert "Query failed" in str(exc_info.value)

@patch('backend.core.config.settings')
def test_factory_function(mock_settings, mock_postgres_settings):
    """Test the factory function."""
    # Configure mock settings
    mock_settings.postgres.host = mock_postgres_settings['host']
    mock_settings.postgres.database = mock_postgres_settings['database']
    mock_settings.postgres.user = mock_postgres_settings['user']
    mock_settings.postgres.password = mock_postgres_settings['password']
    mock_settings.postgres.port = mock_postgres_settings['port']
    
    with patch('backend.db.postgres.PostgresConnector') as mock_connector:
        connector = get_postgres_connector()
        mock_connector.assert_called_once_with(
            host=mock_postgres_settings['host'],
            database=mock_postgres_settings['database'],
            user=mock_postgres_settings['user'],
            password=mock_postgres_settings['password'],
            port=mock_postgres_settings['port']
        ) 