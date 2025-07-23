"""Web search connector using Tavily API."""

import requests
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from functools import lru_cache

from backend.core.config import settings

logger = logging.getLogger(__name__)

class WebSearchConnector:
    """Connector for Tavily web search API."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.tavily.com/v1"):
        """Initialize the web search connector."""
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    @lru_cache(maxsize=100, ttl=1800)  # Cache for 30 minutes
    def search(self,
              query: str,
              search_depth: str = "basic",
              max_results: int = 5,
              include_images: bool = False,
              include_answer: bool = True) -> Dict[str, Any]:
        """Perform a web search using Tavily API."""
        try:
            response = requests.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json={
                    "query": query,
                    "search_depth": search_depth,
                    "max_results": max_results,
                    "include_images": include_images,
                    "include_answer": include_answer
                }
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Add timestamp for cache invalidation purposes
            result["timestamp"] = datetime.now().isoformat()
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Web search failed: {str(e)}")
            raise
            
    def get_answer(self, query: str) -> str:
        """Get a direct answer to a question using Tavily's AI."""
        result = self.search(
            query=query,
            max_results=3,  # Limit results for faster response
            include_answer=True
        )
        return result.get("answer", "No direct answer available.")

# Global connector instance
web_search = WebSearchConnector(
    api_key=settings.web_search.tavily_api_key,
    base_url=settings.web_search.base_url
) 