import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from src.config import settings

# NOTE: In a real scenario, you would configure Ragas to use Azure OpenAI explicitly here.
# Ragas uses OpenAI/LangChain under the hood, so environment variables need to be set correctly.
# Azure configuration for Ragas can be tricky depending on version, often requiring specific
# env vars like OPENAI_API_TYPE="azure", etc.

class RAGEvaluator:
    def __init__(self):
        # Ensure env vars are set for Ragas to pick up Azure
        os.environ["OPENAI_API_TYPE"] = "azure"
        os.environ["OPENAI_API_VERSION"] = settings.AZURE_OPENAI_API_VERSION
        os.environ["OPENAI_API_KEY"] = settings.AZURE_OPENAI_API_KEY
        os.environ["AZURE_OPENAI_ENDPOINT"] = settings.AZURE_OPENAI_ENDPOINT_EU

    def evaluate_dataset(self, questions: list[str], answers: list[str], contexts: list[list[str]], ground_truths: list[list[str]]):
        data = {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths
        }
        dataset = Dataset.from_dict(data)
        
        results = evaluate(
            dataset = dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
            ],
        )
        return results
