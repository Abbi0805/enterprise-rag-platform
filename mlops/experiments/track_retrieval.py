"""
MLflow Experiment Tracking for Retrieval Experiments

Track different retrieval strategies, reranking configs, and model variations.
"""

import mlflow
from mlflow import log_metric, log_param, log_artifact
from typing import Dict, Any, List
import json
import os
from datetime import datetime
from src.config import settings


class RAGExperiment:
    """Wrapper for MLflow experiment tracking in RAG context."""
    
    def __init__(self, experiment_name: str = "rag-retrieval-optimization"):
        self.experiment_name = experiment_name
        
        # Set tracking URI (local or Azure ML workspace)
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "./mlruns")
        mlflow.set_tracking_uri(tracking_uri)
        
        # Create or get experiment
        mlflow.set_experiment(experiment_name)
    
    def run_experiment(
        self,
        experiment_config: Dict[str, Any],
        metrics: Dict[str, float],
        artifacts: Dict[str, str] = None,
    ):
        """
        Log a single experimental run.
        
        Args:
            experiment_config: Configuration parameters (model, chunk_size, etc.)
            metrics: Evaluation metrics (recall@k, MRR, cost, latency, etc.)
            artifacts: Paths to artifacts to log (predictions, examples, etc.)
        """
        with mlflow.start_run(run_name=experiment_config.get("run_name")):
            # Log parameters
            for key, value in experiment_config.items():
                log_param(key, value)
            
            # Log metrics
            for key, value in metrics.items():
                log_metric(key, value)
            
            # Log artifacts
            if artifacts:
                for name, path in artifacts.items():
                    if os.path.exists(path):
                        log_artifact(path, artifact_path=name)
            
            # Log system info
            log_param("timestamp", datetime.utcnow().isoformat())
            log_param("embeddings_model", settings.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT)
            log_param("chat_model", settings.DEFAULT_CHAT_MODEL)


def compare_retrieval_strategies():
    """Example: Compare different retrieval configurations."""
    import random
    
    experiment = RAGExperiment("retrieval-strategy-comparison")
    
    configs = [
        {"name": "vector-only", "use_reranking": False, "top_k": 5},
        {"name": "vector-with-reranking", "use_reranking": True, "top_k": 10},
        {"name": "hybrid-reranked", "use_reranking": True, "top_k": 15}
    ]
    
    print("Running MLflow experiment tracking demo...")
    
    for config in configs:
        print(f"Running: {config['name']}")
        
        # Simulate evaluation metrics (in real scenario, would run actual evaluation)
        simulated_results = {
            "recall_at_5": random.uniform(0.75, 0.95),
            "mrr": random.uniform(0.70, 0.90),
            "latency_ms": random.uniform(400, 1200),
            "cost_per_query": random.uniform(0.003, 0.015),
        }
        
        # Log to MLflow
        experiment.run_experiment(
            experiment_config={
                "run_name": config["name"],
                **config,
            },
            metrics=simulated_results
        )
        print(f"  ✓ Logged metrics: Recall@5={simulated_results['recall_at_5']:.3f}, MRR={simulated_results['mrr']:.3f}")
    
    print(f"\n✅ Experiment complete! View results at: http://localhost:5000")


if __name__ == "__main__":
    # Example usage - simplified demo
    compare_retrieval_strategies()
