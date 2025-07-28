"""Web search service connector."""
import requests
from typing import Dict, Any, List
from cachetools import TTLCache
from functools import wraps
import json

from backend.core.config import get_settings

# Cache for search results (TTL: 1 hour)
_cache = TTLCache(maxsize=100, ttl=3600)

def make_hashable(value):
    """Convert a value to a hashable type."""
    if isinstance(value, (list, tuple)):
        return tuple(make_hashable(x) for x in value)
    elif isinstance(value, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in value.items()))
    elif isinstance(value, (str, int, float, bool, type(None))):
        return value
    return str(value)

def cache_result(func):
    """Cache decorator that handles unhashable arguments."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Make all arguments hashable
        hashable_args = tuple(make_hashable(arg) for arg in args)
        hashable_kwargs = {k: make_hashable(v) for k, v in kwargs.items()}
        
        # Create a unique key for the cache
        key = (func.__name__, hashable_args, tuple(sorted(hashable_kwargs.items())))
        
        if key not in _cache:
            _cache[key] = func(*args, **kwargs)
        return _cache[key]
    return wrapper

class WebSearchConnector:
    """Web search connector with caching."""
    
    def __init__(self):
        """Initialize the connector with settings."""
        self.settings = get_settings().web_search
        self.base_url = "https://api.tavily.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json"
        }
    
    @cache_result
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform a web search."""
        if get_settings().testing:
            return [
                {
                    "title": f"Test Result 1 for: {query}",
                    "url": "https://example.com/1",
                    "content": "This is a test search result."
                },
                {
                    "title": f"Test Result 2 for: {query}",
                    "url": "https://example.com/2",
                    "content": "This is another test search result."
                }
            ]
            
        response = requests.post(
            f"{self.base_url}/search",
            headers=self.headers,
            json={
                "query": query,
                "max_results": max_results,
                "include_answer": False
            }
        )
        response.raise_for_status()
        
        results = response.json()
        return results.get("results", [])
    
    @cache_result
    def get_answer(self, query: str) -> str:
        """Get an AI-generated answer for a query."""
        if get_settings().testing:
            return f"This is a test answer for: {query}"
            
        response = requests.post(
            f"{self.base_url}/search",
            headers=self.headers,
            json={
                "query": query,
                "max_results": 5,
                "include_answer": True
            }
        )
        response.raise_for_status()
        
        results = response.json()
        return results.get("answer", "No answer available.")

# Global connector instance
_web_search_connector = None

def get_web_search_connector() -> WebSearchConnector:
    """Get the global web search connector instance."""
    global _web_search_connector
    if not _web_search_connector:
        _web_search_connector = WebSearchConnector()
    return _web_search_connector 