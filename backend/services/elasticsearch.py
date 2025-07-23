"""Elasticsearch connector for document search and vector operations."""

from elasticsearch import Elasticsearch
from typing import List, Dict, Any, Optional
import logging
from functools import lru_cache

from backend.core.config import settings

logger = logging.getLogger(__name__)

class ElasticsearchConnector:
    """Connector for IBM Cloud Elasticsearch service."""
    
    def __init__(self,
                 host: str,
                 api_key: str,
                 index_name: str = "documents",
                 verify_certs: bool = True):
        """Initialize the Elasticsearch connector."""
        self.host = host
        self.index_name = index_name
        
        # Initialize the client with API key authentication
        self.client = Elasticsearch(
            hosts=[self.host],
            api_key=api_key,
            verify_certs=verify_certs
        )
        
    @lru_cache(maxsize=100, ttl=3600)  # Cache for 1 hour
    def semantic_search(self, 
                       query_vector: List[float],
                       k: int = 5,
                       min_score: float = 0.7) -> List[Dict[str, Any]]:
        """Perform semantic search using vector similarity."""
        try:
            response = self.client.search(
                index=self.index_name,
                body={
                    "size": k,
                    "query": {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                "params": {"query_vector": query_vector}
                            }
                        }
                    },
                    "min_score": min_score
                }
            )
            
            return [{
                "content": hit["_source"]["content"],
                "metadata": hit["_source"].get("metadata", {}),
                "score": hit["_score"]
            } for hit in response["hits"]["hits"]]
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            raise
            
    def keyword_search(self,
                      query: str,
                      fields: List[str] = ["content", "title"],
                      k: int = 5) -> List[Dict[str, Any]]:
        """Perform keyword-based search."""
        try:
            response = self.client.search(
                index=self.index_name,
                body={
                    "size": k,
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": fields,
                            "type": "best_fields",
                            "operator": "and"
                        }
                    }
                }
            )
            
            return [{
                "content": hit["_source"]["content"],
                "metadata": hit["_source"].get("metadata", {}),
                "score": hit["_score"]
            } for hit in response["hits"]["hits"]]
            
        except Exception as e:
            logger.error(f"Keyword search failed: {str(e)}")
            raise
            
    def close(self):
        """Close the Elasticsearch client."""
        self.client.close()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Global connector instance
elasticsearch = ElasticsearchConnector(
    host=settings.elasticsearch.host,
    api_key=settings.elasticsearch.api_key,
    index_name=settings.elasticsearch.index_name,
    verify_certs=settings.elasticsearch.verify_certs
) 