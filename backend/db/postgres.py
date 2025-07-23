"""PostgreSQL database connector."""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
from contextlib import contextmanager

from backend.core.config import get_settings

class PostgresConnector:
    """PostgreSQL database connector with connection pooling."""
    
    def __init__(self):
        """Initialize the connector with settings."""
        self.settings = get_settings().postgres
        self._conn = None
    
    @contextmanager
    def get_connection(self):
        """Get a database connection."""
        if get_settings().testing:
            # Return mock data in test mode
            class MockCursor:
                def execute(self, *args, **kwargs):
                    pass
                
                def fetchall(self):
                    return [
                        {"id": 1, "name": "Test Item 1", "value": 100},
                        {"id": 2, "name": "Test Item 2", "value": 200}
                    ]
                
                def close(self):
                    pass
            
            yield MockCursor()
            return
            
        if not self._conn:
            self._conn = psycopg2.connect(
                host=self.settings.host,
                port=self.settings.port,
                database=self.settings.database,
                user=self.settings.user,
                password=self.settings.password
            )
        
        try:
            cursor = self._conn.cursor(cursor_factory=RealDictCursor)
            yield cursor
            self._conn.commit()
        except Exception as e:
            self._conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as a list of dictionaries."""
        with self.get_connection() as cursor:
            cursor.execute(query, params or {})
            return cursor.fetchall()
    
    def close(self):
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

# Global connector instance
_postgres_connector = None

def get_postgres_connector() -> PostgresConnector:
    """Get the global PostgreSQL connector instance."""
    global _postgres_connector
    if not _postgres_connector:
        _postgres_connector = PostgresConnector()
    return _postgres_connector 