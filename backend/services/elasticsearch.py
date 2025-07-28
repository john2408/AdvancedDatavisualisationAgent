"""Elasticsearch service connector."""
from elasticsearch import Elasticsearch
from typing import List, Dict, Any
from cachetools import TTLCache, keys
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

class ElasticsearchConnector:
    """Elasticsearch connector with caching."""
    
    def __init__(self):
        """Initialize the connector with settings."""
        self.settings = get_settings().elasticsearch
        if not get_settings().testing:
            self.client = Elasticsearch(
                self.settings.host,
                api_key=self.settings.api_key
            )
        else:
            self.client = None
    
    @cache_result
    def semantic_search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search using vector similarity."""
        if get_settings().testing:
            return [
                {"id": "1", "content": "Test Document 1", "score": 0.95},
                {"id": "2", "content": "Test Document 2", "score": 0.85}
            ]
            
        query = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            },
            "size": k
        }
        
        response = self.client.search(
            index=self.settings.index_name,
            body=query
        )
        
        return [
            {
                "id": hit["_id"],
                "content": hit["_source"].get("content", ""),
                "score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]
    
    @cache_result
    def keyword_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Perform keyword-based search."""
        if get_settings().testing:
            return [
                {"id": "1", "content": f"Test Result 1 for: {query}", "score": 0.95},
                {"id": "2", "content": f"Test Result 2 for: {query}", "score": 0.85}
            ]
            
        query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["content^2", "title"],
                    "type": "best_fields"
                }
            },
            "size": k
        }
        
        response = self.client.search(
            index=self.settings.index_name,
            body=query
        )
        
        return [
            {
                "id": hit["_id"],
                "content": hit["_source"].get("content", ""),
                "score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]

# Global connector instance
_elasticsearch_connector = None

def get_elasticsearch_connector() -> ElasticsearchConnector:
    """Get the global Elasticsearch connector instance."""
    global _elasticsearch_connector
    if not _elasticsearch_connector:
        _elasticsearch_connector = ElasticsearchConnector()
    return _elasticsearch_connector 