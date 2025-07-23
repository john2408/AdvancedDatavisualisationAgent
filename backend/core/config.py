"""Configuration management for backend services."""

from pathlib import Path
from typing import Dict, Any
import os
import toml
from pydantic import BaseSettings, Field

class PostgresSettings(BaseSettings):
    """PostgreSQL connection settings."""
    host: str = Field(..., description="Database host")
    database: str = Field(..., description="Database name")
    user: str = Field(..., description="Database user")
    password: str = Field(..., description="Database password")
    port: int = Field(5432, description="Database port")
    
    class Config:
        env_prefix = "POSTGRES_"

class ElasticsearchSettings(BaseSettings):
    """Elasticsearch connection settings."""
    host: str = Field(..., description="Elasticsearch host URL")
    api_key: str = Field(..., description="API key for authentication")
    index_name: str = Field("documents", description="Index name")
    verify_certs: bool = Field(True, description="Verify SSL certificates")
    
    class Config:
        env_prefix = "ES_"

class WebSearchSettings(BaseSettings):
    """Web search API settings."""
    tavily_api_key: str = Field(..., description="Tavily API key")
    base_url: str = Field("https://api.tavily.com/v1", description="API base URL")
    
    class Config:
        env_prefix = "WEBSEARCH_"

class Settings(BaseSettings):
    """Global settings container."""
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    elasticsearch: ElasticsearchSettings = Field(default_factory=ElasticsearchSettings)
    web_search: WebSearchSettings = Field(default_factory=WebSearchSettings)
    
    @classmethod
    def from_streamlit_secrets(cls, secrets_path: Path) -> "Settings":
        """Create settings from Streamlit secrets file."""
        if not secrets_path.exists():
            raise FileNotFoundError(f"Secrets file not found: {secrets_path}")
            
        secrets = toml.load(secrets_path)
        
        return cls(
            postgres=PostgresSettings(**secrets.get("postgres", {})),
            elasticsearch=ElasticsearchSettings(**secrets.get("elasticsearch", {})),
            web_search=WebSearchSettings(**secrets.get("web_search", {}))
        )

# Global settings instance
settings = Settings() 