"""PostgreSQL connector with connection pooling."""

import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
import logging
from functools import lru_cache

from backend.core.config import settings

logger = logging.getLogger(__name__)

class PostgresConnector:
    """A PostgreSQL connector with connection pooling."""
    
    def __init__(self, 
                 host: str,
                 database: str,
                 user: str,
                 password: str,
                 port: int = 5432,
                 min_conn: int = 1,
                 max_conn: int = 10):
        """Initialize the PostgreSQL connector."""
        self.conn_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }
        
        self.pool = SimpleConnectionPool(
            minconn=min_conn,
            maxconn=max_conn,
            **self.conn_params,
            cursor_factory=RealDictCursor
        )
        
    @lru_cache(maxsize=1)
    def get_connection(self):
        """Get a connection from the pool."""
        return self.pool.getconn()
        
    def return_connection(self, conn):
        """Return a connection to the pool."""
        self.pool.putconn(conn)
        
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a read-only query and return results."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")
                cur.execute(query, params)
                results = cur.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise
        finally:
            self.return_connection(conn)
            
    def close(self):
        """Close all connections in the pool."""
        self.pool.closeall()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Global connector instance
postgres = PostgresConnector(
    host=settings.postgres.host,
    database=settings.postgres.database,
    user=settings.postgres.user,
    password=settings.postgres.password,
    port=settings.postgres.port
) 