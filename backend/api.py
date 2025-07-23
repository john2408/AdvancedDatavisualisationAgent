"""API interface for backend services."""

from typing import List, Dict, Any, Optional
from backend.db.postgres import postgres
from backend.services.elasticsearch import elasticsearch
from backend.services.web_search import web_search

class BackendAPI:
    """Interface for accessing backend services."""
    
    @staticmethod
    def query_database(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a database query."""
        return postgres.execute_query(query, params)
    
    @staticmethod
    def semantic_search(query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic document search."""
        return elasticsearch.semantic_search(query_vector, k=k)
    
    @staticmethod
    def keyword_search(query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Perform keyword-based document search."""
        return elasticsearch.keyword_search(query, k=k)
    
    @staticmethod
    def web_search(query: str, max_results: int = 5) -> Dict[str, Any]:
        """Perform web search."""
        return web_search.search(query, max_results=max_results)
    
    @staticmethod
    def get_web_answer(query: str) -> str:
        """Get direct answer from web search."""
        return web_search.get_answer(query)

# Global API instance
api = BackendAPI() 