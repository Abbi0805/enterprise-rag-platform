from typing import List
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from src.types import Chunk, SearchResult
from src.config import settings
import uuid

class VectorStore:
    def __init__(self, collection_name: str = None):
        # Use settings for collection name if not provided
        self.collection_name = collection_name or settings.QDRANT_COLLECTION
        
        # Connect to Qdrant
        if settings.QDRANT_URL:
            print(f"Connecting to Qdrant at {settings.QDRANT_URL}...")
            self.client = AsyncQdrantClient(url=settings.QDRANT_URL)
        else:
            print("Using in-memory Qdrant (Ephemeral)...")
            self.client = AsyncQdrantClient(location=":memory:") 
            
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
            
        if not await self.client.collection_exists(self.collection_name):
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=3072, distance=models.Distance.COSINE) # 3072 for text-embedding-3-large
            )
        self._initialized = True

    async def upsert(self, chunks: List[Chunk]):
        await self.initialize()
        
        points = [
            models.PointStruct(
                id=str(uuid.uuid4()), # Qdrant needs UUID or int
                vector=chunk.embedding,
                payload={
                    "content": chunk.content,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    **chunk.metadata
                }
            )
            for chunk in chunks
            if chunk.embedding
        ]
        
        if points:
            await self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

    async def search(self, query_vector: List[float], limit: int = 10) -> List[SearchResult]:
        await self.initialize()
        
        search_result = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        )
        
        return [
            SearchResult(
                chunk=Chunk(
                    id=hit.id,
                    document_id=hit.payload.get("document_id"),
                    content=hit.payload.get("content"),
                    chunk_index=hit.payload.get("chunk_index"),
                    metadata={k:v for k,v in hit.payload.items() if k not in ["content", "document_id", "chunk_index"]}
                ),
                score=hit.score,
                rank=i
            )
            for i, hit in enumerate(search_result.points)
        ]
