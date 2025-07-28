"""Configuration module for the application."""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class PostgresSettings(BaseSettings):
    """PostgreSQL connection settings."""
    host: str = "localhost"
    port: int = 5432
    database: str = "testdb"
    user: str = "testuser"
    password: str = "testpass"
    
    class Config:
        env_prefix = "POSTGRES_"

class ElasticsearchSettings(BaseSettings):
    """Elasticsearch connection settings."""
    host: str = "http://localhost:9200"
    api_key: str = "test_key"
    index_name: str = "test_index"
    
    class Config:
        env_prefix = "ELASTICSEARCH_"

class WebSearchSettings(BaseSettings):
    """Web search API settings."""
    api_key: str = "test_key"
    
    class Config:
        env_prefix = "TAVILY_"

class Settings(BaseSettings):
    """Global application settings."""
    testing: bool = True
    postgres: PostgresSettings = PostgresSettings()
    elasticsearch: ElasticsearchSettings = ElasticsearchSettings()
    web_search: WebSearchSettings = WebSearchSettings()

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 