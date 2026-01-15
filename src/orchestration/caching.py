from typing import Optional
from src.ingestion.embeddings import EmbeddingGenerator
import numpy as np

class SemanticCache:
    def __init__(self, threshold: float = 0.9):
        # Naive in-memory cache: List of (embedding, answer)
        # In prod: Redis or dedicated vector store
        self.cache = [] 
        self.threshold = threshold
        self.embedding_gen = EmbeddingGenerator()

    async def get(self, query: str) -> Optional[str]:
        if not self.cache:
            return None
            
        query_embedding = (await self.embedding_gen.generate([query]))[0]
        
        best_score = -1
        best_answer = None
        
        for cached_emb, answer in self.cache:
            # Cosine similarity
            score = np.dot(query_embedding, cached_emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(cached_emb))
            if score > best_score:
                best_score = score
                best_answer = answer
                
        if best_score >= self.threshold:
            return best_answer
        return None

    async def set(self, query: str, answer: str):
        query_embedding = (await self.embedding_gen.generate([query]))[0]
        self.cache.append((query_embedding, answer))
