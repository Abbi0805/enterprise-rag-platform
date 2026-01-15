from typing import List
from src.types import Chunk, SearchResult
from src.ingestion.embeddings import EmbeddingGenerator
from src.retrieval.vector import VectorStore
from src.retrieval.keyword import KeywordSearch
from src.retrieval.reranking import ReRanker

class RetrievalService:
    def __init__(self):
        self.embedding_gen = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.keyword_search = KeywordSearch()
        self.reranker = ReRanker()

    async def ingest(self, chunks: List[Chunk]):
        # index for vector
        await self.embedding_gen.embed_chunks(chunks)
        await self.vector_store.upsert(chunks)
        
        # index for keyword
        self.keyword_search.index(chunks) # Note: Naive in-memory implementation for demo

    async def search(self, query: str, user: 'User', limit: int = 10) -> List[SearchResult]:
        # Vector Search
        query_embedding = (await self.embedding_gen.generate([query]))[0]
        vector_results = await self.vector_store.search(query_embedding, limit=limit * 2) # Fetch more for filtering
        
        # Keyword Search
        keyword_results = self.keyword_search.search(query, limit=limit * 2)
        
        # Hybrid Fusion using Reciprocal Rank Fusion (RRF) or simple deduplication
        # Here: Simple deduplication based on chunk content/ID
        seen_ids = set()
        candidates = []
        
        for res in vector_results + keyword_results:
            if res.chunk.id not in seen_ids:
                # Permission Check
                required_group = res.chunk.metadata.get("access_group")
                if user.can_access(required_group):
                    candidates.append(res)
                    seen_ids.add(res.chunk.id)

        
        # Re-ranking
        ranking_results = self.reranker.rerank(query, candidates, top_k=limit)
        
        return ranking_results
