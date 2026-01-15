# 🏗️ Infrastructure as Code (IaC)

This directory contains templates and configurations for deploying the Enterprise RAG Platform to Microsoft Azure.

## 📋 Strategy

The infrastructure is designed to be fully automated using either **Terraform** or **Azure Bicep**.

### 🛠️ Components
The platform requires the following Azure services:
1. **Azure App Service**: To host the FastAPI Backend.
2. **Azure OpenAI Service**: For LLM (GPT-4o) and Embeddings (text-embedding-3-large).
3. **Azure Container Instances (ACI)**: To run the Qdrant Vector Database.
4. **Azure Storage Account**: For persistent log and model storage.
5. **Azure Monitor & App Insights**: For full observability and cost tracking.

---

## 🚀 Deployment Options

### 1. Terraform
Located in [`terraform/`](terraform/). Uses HCL to define cross-cloud resources. Best for teams already using Terraform.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 2. Azure Bicep
Located in [`azure/`](azure/). Native Azure IaC language. Best for deep integration with Azure features and faster deployment cycles.

```bash
cd azure
az deployment sub create --location westeurope --template-file main.bicep
```

---

## 🔒 Security Posture
- **Private Endpoints**: All services operate within a VNet.
- **Managed Identities**: No API keys stored in configuration; services use Entra ID (formerly Azure AD).
- **Key Vault**: For managing external secrets if necessary.
