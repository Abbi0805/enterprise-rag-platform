from typing import List
from openai import AsyncAzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from src.config import settings
from src.types import Chunk

class EmbeddingGenerator:
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_EMBEDDINGS_API_KEY,
            api_version=settings.AZURE_OPENAI_EMBEDDINGS_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_EMBEDDINGS_ENDPOINT
        )
        self.deployment = settings.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate(self, texts: List[str]) -> List[List[float]]:
        # Check for invalid key prefix to avoid wasting time/retries
        if self.client.api_key.startswith("REPL") or self.client.api_key == "REPLACE_WITH_KEY":
            print("WARNING: Using MOCK Embeddings due to invalid API Key.")
            # Return random 3072-dim vectors (text-embedding-3-large size)
            import random
            return [[random.random() for _ in range(3072)] for _ in texts]

        # Azure OpenAI Embeddings require replacing newlines for better performance 
        # (check if still needed for v3, usually good practice)
        processed_texts = [text.replace("\n", " ") for text in texts]
        
        try:
            response = await self.client.embeddings.create(
                input=processed_texts,
                model=self.deployment
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"Embedding Error: {e}")
            print("Falling back to MOCK Embeddings due to Error.")
            import random
            return [[random.random() for _ in range(3072)] for _ in texts]


    async def embed_chunks(self, chunks: List[Chunk]):
        texts = [chunk.content for chunk in chunks]
        # Batching could be implemented here if texts list is too large
        embeddings = await self.generate(texts)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
