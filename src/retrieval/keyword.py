from typing import List
from rank_bm25 import BM25Okapi
from src.types import Chunk, SearchResult

class KeywordSearch:
    def __init__(self):
        self.bm25 = None
        self.chunks = []

    def index(self, chunks: List[Chunk]):
        self.chunks = chunks
        tokenized_corpus = [chunk.content.split(" ") for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        if not self.bm25:
            return []
            
        tokenized_query = query.split(" ")
        doc_scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_n = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:limit]
        
        return [
            SearchResult(
                chunk=self.chunks[i],
                score=doc_scores[i],
                rank=idx
            )
            for idx, i in enumerate(top_n)
            if doc_scores[i] > 0
        ]
