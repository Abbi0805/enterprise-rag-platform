from abc import ABC, abstractmethod
from typing import List
import tiktoken
from src.types import Document, Chunk

class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]:
        pass

class FixedSizeChunker(BaseChunker):
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: Document) -> List[Chunk]:
        text = document.content
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            chunks.append(Chunk(
                document_id=document.id,
                content=chunk_text,
                chunk_index=len(chunks),
                metadata=document.metadata
            ))
            
            start += self.chunk_size - self.overlap
            
        return chunks

class RecursiveTokenChunker(BaseChunker):
    def __init__(self, chunk_size: int = 500, overlap: int = 50, model_name: str = "gpt-4"):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.encoder = tiktoken.encoding_for_model(model_name)

    def chunk(self, document: Document) -> List[Chunk]:
        tokens = self.encoder.encode(document.content)
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoder.decode(chunk_tokens)
            
            chunks.append(Chunk(
                document_id=document.id,
                content=chunk_text,
                chunk_index=len(chunks),
                metadata=document.metadata
            ))
            
            start += self.chunk_size - self.overlap
            
        return chunks
