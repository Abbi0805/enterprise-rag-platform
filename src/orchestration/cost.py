import tiktoken
from typing import Dict

class CostTracker:
    # Pricing per 1k tokens (approximate as of early 2024 for Azure/OpenAI)
    PRICING = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "text-embedding-3-large": {"input": 0.000143, "output": 0.0},
    }


    def __init__(self):
        self.total_cost = 0.0
        self.request_costs: Dict[str, float] = {} # request_id -> cost of that request

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        prices = self.PRICING.get(model)
        if not prices:
            return 0.0
            
        input_cost = (input_tokens / 1000) * prices["input"]
        output_cost = (output_tokens / 1000) * prices["output"]
        
        return input_cost + output_cost

    def track(self, model: str, input_text: str, output_text: str, request_id: str = "global"):
        # Estimate tokens (using cl100k_base which is common for gpt-4)
        enc = tiktoken.get_encoding("cl100k_base")
        input_tokens = len(enc.encode(input_text))
        output_tokens = len(enc.encode(output_text))
        
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        
        self.total_cost += cost
        self.request_costs[request_id] = self.request_costs.get(request_id, 0.0) + cost
        
        print(f"[CostTracker] Request: {request_id} | Model: {model} | Cost: ${cost:.6f}") # Log it

    def track_request(self, model: str, input_tokens: int, output_tokens: int, user_id: str = "global"):
        """Track cost using known token counts from API response"""
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        self.total_cost += cost
        # We could track per user here if we wanted
        print(f"[CostTracker] User: {user_id} | Model: {model} | In: {input_tokens} Out: {output_tokens} | Cost: ${cost:.6f}")

cost_tracker = CostTracker()
