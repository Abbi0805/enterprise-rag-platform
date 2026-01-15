from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

class Document(BaseModel):
    """Represents a source document before chunking."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Chunk(BaseModel):
    """Represents a chunk of text for retrieval."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunk_index: int

class SearchResult(BaseModel):
    """Represents a retrieved chunk with score."""
    chunk: Chunk
    score: float
    rank: int
