from jinja2 import Template
from typing import Dict, Any
from src.retrieval.service import RetrievalService
from src.orchestration.llm import LLMClient
from src.orchestration.prompts import SYSTEM_PROMPT, USER_PROMPT
from src.orchestration.caching import SemanticCache

from src.auth.models import User

class RAGOrchestrator:
    def __init__(self):
        self.retriever = RetrievalService()
        self.llm = LLMClient()
        self.cache = SemanticCache()

    async def query(self, user_query: str, user: User) -> Dict[str, Any]:
        # 1. Check Cache
        cached_answer = await self.cache.get(user_query)
        if cached_answer:
            return {
                "answer": cached_answer,
                "source": "cache",
                "retrieved_docs": []
            }

        # 2. Retrieve
        results = await self.retriever.search(user_query, user, limit=5)
        
        # 3. Assemble Context
        context_text = "\n\n".join([f"Source ({r.chunk.metadata.get('source', 'unknown')}): {r.chunk.content}" for r in results])
        
        system_message = Template(SYSTEM_PROMPT).render(context=context_text)
        user_message = Template(USER_PROMPT).render(question=user_query)
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

        # 4. Generate
        answer = await self.llm.generate_completion(messages)
        
        # 5. Cache (in background ideally)
        await self.cache.set(user_query, answer)

        return {
            "answer": answer,
            "source": "llm",
            "retrieved_docs": [r.dict() for r in results]
        }
