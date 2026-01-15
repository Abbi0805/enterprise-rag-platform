from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Azure OpenAI - Chat / Reasoning
    AZURE_OPENAI_API_KEY: str = Field(..., description="API Key for Azure OpenAI")
    AZURE_OPENAI_API_VERSION: str = Field(default="2024-12-01-preview")
    AZURE_OPENAI_ENDPOINT_EU: str = Field(..., description="Endpoint for Chat Models")
    AZURE_OPENAI_GPT4O_DEPLOYMENT: str = Field(default="gpt-4o-prod")
    AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT: str = Field(default="gpt-4o-mini")

    # Azure OpenAI - Embeddings
    AZURE_OPENAI_EMBEDDINGS_API_KEY: str = Field(..., description="API Key for Embeddings Resource")
    AZURE_OPENAI_EMBEDDINGS_ENDPOINT: str = Field(..., description="Endpoint for Embeddings")
    AZURE_OPENAI_EMBEDDINGS_API_VERSION: str = Field(default="2024-02-01")
    AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT: str = Field(default="text-embedding-3-large")

    # Project Defaults
    DEFAULT_CHAT_MODEL: str = Field(default="gpt-4o-mini")
    FALLBACK_CHAT_MODEL: str = Field(default="gpt-4o")

    # Vector Store
    QDRANT_URL: Optional[str] = Field(default=None, description="URL for Qdrant (e.g. http://localhost:6333). If None, uses :memory:")
    QDRANT_COLLECTION: str = Field(default="enterprise-rag", description="Name of the Qdrant collection")

settings = Settings()
