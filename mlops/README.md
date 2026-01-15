# MLOps Setup Guide

## Prerequisites
1. **Azure Subscription** with Azure ML Workspace created
2. **Service Principal** or **Managed Identity** for authentication
3. **Compute Cluster** named `cpu-cluster` in your workspace

## Step 1: Configure Workspace

Edit `.env` with your workspace details:

```env
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-rg-name
AZURE_ML_WORKSPACE=your-workspace-name
```

## Step 2: Authenticate

```bash
# Login to Azure
az login

# Set default subscription
az account set --subscription YOUR_SUBSCRIPTION_ID
```

## Step 3: Create Golden Dataset

```bash
python mlops/datasets/manage_golden_dataset.py
```

This creates `mlops/datasets/golden_qa.json` with sample questions.

## Step 4: Upload Dataset to Azure ML

```bash
az ml data create --name golden-qa-v1 \
  --path mlops/datasets/golden_qa.json \
  --type uri_file
```

## Step 5: Submit Evaluation Pipeline

```bash
python mlops/pipelines/evaluation_pipeline.py
```

Monitor in Azure ML Studio at the printed URL.

## Step 6: Run Local Experiments

```bash
python mlops/experiments/track_retrieval.py
```

View results with `mlflow ui` at `http://localhost:5000`.

## MLflow Tracking

Set tracking URI for Azure ML integration:

```bash
export MLFLOW_TRACKING_URI=azureml:///<subscription_id>/<rg>/<workspace>
```

Or use local tracking (default):
```bash
# Runs will be logged to ./mlruns
mlflow ui
```

## Continuous Evaluation (GitHub Actions)

The workflow `.github/workflows/eval.yml` triggers on:
- Every push to `main`
- Manual trigger via GitHub UI

Configure repository secrets:
- `AZURE_CREDENTIALS`
- `AZURE_SUBSCRIPTION_ID`
- etc.
