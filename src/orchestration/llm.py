from openai import AsyncAzureOpenAI
from src.config import settings
from typing import List, Dict, Any
from src.orchestration.cost import cost_tracker

class LLMClient:
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT_EU
        )
        self.deployment = settings.AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT
        self.cost_tracker = cost_tracker

    async def generate_completion(self, messages: list, user_id: str = None) -> str:
        # Check for invalid key prefix
        if self.client.api_key.startswith("REPL") or self.client.api_key == "REPLACE_WITH_KEY":
            return "This is a MOCK response. The system is working, but your Azure OpenAI API Key is invalid in .env."

        try:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=messages
            )
            
            # Extract answer
            answer = response.choices[0].message.content
            
            # Track cost
            if self.cost_tracker:
                self.cost_tracker.track_request(
                    model=self.deployment,
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    user_id=user_id
                )
                
            return answer
        except Exception as e:
            print(f"LLM Error: {e}")
            if "401" in str(e) or "Access Denied" in str(e):
                return "MOCK RESPONSE: Authentication failed with Azure OpenAI. Please check your API Key."
            raise e
