from typing import List
from sentence_transformers import CrossEncoder
from src.types import SearchResult, Chunk

class ReRanker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        # In a real app, load this once globally or use an external service
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, results: List[SearchResult], top_k: int = 5) -> List[SearchResult]:
        if not results:
            return []
            
        inputs = [[query, res.chunk.content] for res in results]
        scores = self.model.predict(inputs)
        
        # Update scores and sort
        for res, score in zip(results, scores):
            res.score = float(score)
            
        # Sort by score descending
        reranked = sorted(results, key=lambda x: x.score, reverse=True)
        
        # Update ranks and slice
        final_results = []
        for i, res in enumerate(reranked[:top_k]):
            res.rank = i
            final_results.append(res)
            
        return final_results
