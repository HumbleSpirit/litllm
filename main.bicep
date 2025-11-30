// Parameters
param location string = resourceGroup().location
param openaiName string = 'litellm-openai-${uniqueString(resourceGroup().id)}'
param acrName string = 'litellmacr${uniqueString(resourceGroup().id)}'
param appPlanName string = 'litellm-plan'
param webAppName string = 'litellm-${uniqueString(resourceGroup().id)}'

// Azure OpenAI Resource
resource openai 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openaiName
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: openaiName
    publicNetworkAccess: 'Enabled'
  }
}

// GPT-4 Deployment (using gpt-4o)
resource gpt4Deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openai
  name: 'gpt-4'
  sku: {
    name: 'Standard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-11-20'
    }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
  }
}

// GPT-3.5 Deployment (using gpt-4o-mini)
resource gpt35Deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openai
  name: 'gpt-35-turbo'
  sku: {
    name: 'GlobalStandard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o-mini'
      version: '2024-07-18'
    }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
  }
  dependsOn: [
    gpt4Deployment
  ]
}

// Container Registry
resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: acrName
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    adminUserEnabled: true
  }
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appPlanName
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// Web App
resource webApp 'Microsoft.Web/sites@2022-09-01' = {
  name: webAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|${acr.properties.loginServer}/litellm:latest'
      appSettings: [
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: 'https://${acr.properties.loginServer}'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_USERNAME'
          value: acr.listCredentials().username
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_PASSWORD'
          value: acr.listCredentials().passwords[0].value
        }
        {
          name: 'WEBSITES_PORT'
          value: '8080'
        }
        {
          name: 'LITELLM_VERBOSE'
          value: 'True'
        }
        {
          name: 'DEFAULT_MODEL'
          value: 'azure/gpt-4'
        }
        {
          name: 'AZURE_API_KEY'
          value: openai.listKeys().key1
        }
        {
          name: 'AZURE_API_BASE'
          value: openai.properties.endpoint
        }
        {
          name: 'AZURE_API_VERSION'
          value: '2024-02-15-preview'
        }
        {
          name: 'AZURE_FOUNDRY_API_KEY'
          value: openai.listKeys().key1
        }
        {
          name: 'AZURE_FOUNDRY_API_BASE'
          value: openai.properties.endpoint
        }
        {
          name: 'AZURE_FOUNDRY_API_VERSION'
          value: '2024-02-15-preview'
        }
        {
          name: 'AZURE_GPT4_DEPLOYMENT'
          value: 'gpt-4'
        }
        {
          name: 'AZURE_GPT5_DEPLOYMENT'
          value: 'gpt-35-turbo'
        }
      ]
    }
  }
}

// Outputs
output openaiEndpoint string = openai.properties.endpoint
output openaiKey string = openai.listKeys().key1
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output acrLoginServer string = acr.properties.loginServer
