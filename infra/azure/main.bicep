// =============================================================================
// Azure Bicep Skeleton for Enterprise RAG Platform
// =============================================================================

param location string = resourceGroup().location
param appName string = 'app-enterprise-rag'
param openAiName string = 'cog-rag-openai'

// --- Azure OpenAI Service ---
resource openAi 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openAiName
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

// --- App Service Plan ---
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: 'plan-rag-platform'
  location: location
  sku: {
    name: 'P1v2'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// --- Web App ---
resource webApp 'Microsoft.Web/sites@2022-09-01' = {
  name: appName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AZURE_OPENAI_ENDPOINT'
          value: openAi.properties.endpoint
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
      ]
    }
  }
}

output endpoint string = webApp.properties.defaultHostName
