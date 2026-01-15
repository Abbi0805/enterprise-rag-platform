"""
Azure ML Pipeline for RAG Evaluation

This module defines an Azure ML pipeline that:
1. Loads a golden dataset from Azure ML Datasets
2. Runs retrieval and generation on each query
3. Evaluates results using RAGAS metrics
4. Logs metrics to MLflow
"""

from azure.ai.ml import MLClient, Input, Output
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import command
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Environment
import os


def get_ml_client():
    """Initialize Azure ML client from environment variables."""
    from dotenv import load_dotenv
    load_dotenv()
    
    credential = DefaultAzureCredential()
    ml_client = MLClient(
        credential=credential,
        subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
        resource_group_name=os.getenv("AZURE_RESOURCE_GROUP"),
        workspace_name=os.getenv("AZURE_ML_WORKSPACE"),
    )
    return ml_client


@pipeline(
    name="rag_evaluation_pipeline",
    description="Evaluate RAG system quality using RAGAS metrics",
    compute="cpu-cluster",  # Replace with your compute cluster name
)
def rag_evaluation_pipeline(
    golden_dataset: Input(type="uri_file"),
    embeddings_endpoint: str,
    embeddings_key: str,
    chat_endpoint: str,
    chat_key: str,
):
    """
    RAG Evaluation Pipeline
    
    Args:
        golden_dataset: Path to JSON file with queries and expected answers
        embeddings_endpoint: Azure OpenAI embeddings endpoint
        embeddings_key: Azure OpenAI embeddings key
        chat_endpoint: Azure OpenAI chat endpoint
        chat_key: Azure OpenAI chat key
    """
    
    # Define environment
    environment = Environment(
        name="rag-evaluation-env",
        description="Environment for RAG evaluation",
        conda_file="mlops/pipelines/conda.yml",
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
    )
    
    # Step 1: Run RAG queries
    rag_inference_step = command(
        name="rag_inference",
        display_name="Run RAG Inference",
        code="./",  # Project root
        command="""
        python mlops/pipelines/steps/run_inference.py \
            --golden-dataset ${{inputs.golden_dataset}} \
            --embeddings-endpoint ${{inputs.embeddings_endpoint}} \
            --embeddings-key ${{inputs.embeddings_key}} \
            --chat-endpoint ${{inputs.chat_endpoint}} \
            --chat-key ${{inputs.chat_key}} \
            --output-dir ${{outputs.predictions}}
        """,
        inputs={
            "golden_dataset": golden_dataset,
            "embeddings_endpoint": embeddings_endpoint,
            "embeddings_key": embeddings_key,
            "chat_endpoint": chat_endpoint,
            "chat_key": chat_key,
        },
        outputs={"predictions": Output(type="uri_folder")},
        environment=environment,
    )
    
    # Step 2: Evaluate with RAGAS
    evaluation_step = command(
        name="evaluate_ragas",
        display_name="Evaluate with RAGAS",
        code="./",
        command="""
        python mlops/pipelines/steps/evaluate.py \
            --predictions-dir ${{inputs.predictions}} \
            --output-metrics ${{outputs.metrics}}
        """,
        inputs={"predictions": rag_inference_step.outputs.predictions},
        outputs={"metrics": Output(type="uri_file")},
        environment=environment,
    )
    
    return {
        "predictions": rag_inference_step.outputs.predictions,
        "metrics": evaluation_step.outputs.metrics,
    }


def submit_pipeline():
    """Submit the evaluation pipeline to Azure ML."""
    ml_client = get_ml_client()
    
    # Create pipeline instance
    pipeline_job = rag_evaluation_pipeline(
        golden_dataset=Input(
            type="uri_file",
            path="azureml://datastores/workspaceblobstore/paths/golden_qa.json"
        ),
        embeddings_endpoint=os.getenv("AZURE_OPENAI_EMBEDDINGS_ENDPOINT"),
        embeddings_key=os.getenv("AZURE_OPENAI_EMBEDDINGS_API_KEY"),
        chat_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_EU"),
        chat_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )
    
    # Submit job
    pipeline_job = ml_client.jobs.create_or_update(
        pipeline_job, experiment_name="rag-evaluation"
    )
    
    print(f"Pipeline submitted: {pipeline_job.name}")
    print(f"Studio URL: {pipeline_job.studio_url}")
    
    return pipeline_job


if __name__ == "__main__":
    job = submit_pipeline()
