"""
Golden Dataset Management for RAG Evaluation

Create and version datasets for regression testing and evaluation.
"""

import json
from typing import List, Dict
from pathlib import Path
from datetime import datetime


class GoldenDataset:
    """Manages golden question-answer pairs for RAG evaluation."""
    
    def __init__(self, dataset_path: str = "mlops/datasets/golden_qa.json"):
        self.dataset_path = Path(dataset_path)
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        self.examples: List[Dict] = []
        
        if self.dataset_path.exists():
            self.load()
    
    def add_example(
        self,
        question: str,
        expected_answer: str,
        expected_sources: List[str] = None,
        category: str = "general",
        metadata: Dict = None
    ):
        """Add a golden example to the dataset."""
        example = {
            "id": len(self.examples),
            "question": question,
            "expected_answer": expected_answer,
            "expected_sources": expected_sources or [],
            "category": category,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        self.examples.append(example)
    
    def save(self, version: str = None):
        """Save dataset to file."""
        data = {
            "version": version or datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
            "created_at": datetime.utcnow().isoformat(),
            "num_examples": len(self.examples),
            "examples": self.examples,
        }
        
        with open(self.dataset_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(self.examples)} examples to {self.dataset_path}")
    
    def load(self):
        """Load dataset from file."""
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.examples = data.get("examples", [])
        print(f"Loaded {len(self.examples)} examples (version: {data.get('version')})")
        
        return self.examples
    
    def export_for_ragas(self, output_path: str = "mlops/datasets/ragas_eval.json"):
        """Export in RAGAS-compatible format."""
        ragas_data = {
            "questions": [ex["question"] for ex in self.examples],
            "ground_truths": [[ex["expected_answer"]] for ex in self.examples],
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(ragas_data, f, indent=2)
        
        print(f"Exported RAGAS dataset to {output_path}")


def create_sample_dataset():
    """Create a sample golden dataset for CV/recruiter questions."""
    dataset = GoldenDataset()
    
    # Example questions for a CV-based RAG system
    dataset.add_example(
        question="What experience does this person have with RAG systems?",
        expected_answer="The person has extensive experience building enterprise RAG platforms with hybrid retrieval, semantic caching, and cost optimization.",
        category="technical_experience"
    )
    
    dataset.add_example(
        question="Which cloud platforms has this candidate worked with?",
        expected_answer="The candidate has worked with Microsoft Azure, specifically Azure OpenAI, Azure ML, and Azure AI Search.",
        category="cloud_skills"
    )
    
    dataset.add_example(
        question="What MLOps tools does this person know?",
        expected_answer="The candidate has experience with Azure Machine Learning, MLflow for experiment tracking, and CI/CD pipelines with GitHub Actions.",
        category="mlops"
    )
    
    dataset.add_example(
        question="What programming languages is this person proficient in?",
        expected_answer="The person is proficient in Python, with experience in async programming, FastAPI, and modern AI/ML frameworks.",
        category="programming"
    )
    
    dataset.save(version="1.0.0")
    dataset.export_for_ragas()


if __name__ == "__main__":
    create_sample_dataset()
