# =============================================================================
# Terraform Skeleton for Enterprise RAG Platform
# =============================================================================

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-enterprise-rag"
  location = "West Europe"
}

# --- Azure OpenAI Service ---
resource "azurerm_cognitive_account" "openai" {
  name                = "cog-rag-openai"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "OpenAI"
  sku_name            = "S0"
}

# --- Qdrant (Azure Container Instances) ---
resource "azurerm_container_group" "qdrant" {
  name                = "aci-qdrant"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  ip_address_type     = "Public"
  dns_name_label      = "qdrant-db"
  os_type             = "Linux"

  container {
    name   = "qdrant"
    image  = "qdrant/qdrant:latest"
    cpu    = "1"
    memory = "2"

    ports {
      port     = 6333
      protocol = "TCP"
    }

    volume {
      name                 = "qdrant-data"
      mount_path           = "/qdrant/storage"
      read_only            = false
      share_name           = "qdrantdata"
      storage_account_name = "stentragdata"
      storage_account_key  = "PLACEHOLDER"
    }
  }
}

# --- FastAPI App Service ---
resource "azurerm_service_plan" "asp" {
  name                = "asp-rag-platform"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "P1v2"
}

resource "azurerm_linux_web_app" "app" {
  name                = "app-rag-backend"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_service_plan.asp.location
  service_plan_id     = azurerm_service_plan.asp.id

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    "AZURE_OPENAI_ENDPOINT" = azurerm_cognitive_account.openai.endpoint
    "QDRANT_URL"            = "http://${azurerm_container_group.qdrant.fqdn}:6333"
  }
}
