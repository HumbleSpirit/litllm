@description('Name of the container instance')
param containerName string = 'litellm-gateway'

@description('Location for resources')
param location string = resourceGroup().location

@description('Container image to deploy')
param containerImage string = 'your-registry.azurecr.io/litellm-gateway:latest'

@description('CPU cores for the container')
param cpuCores int = 1

@description('Memory in GB')
param memoryInGb int = 2

@description('OpenAI API Key')
@secure()
param openaiApiKey string

@description('Default model to use')
param defaultModel string = 'gpt-3.5-turbo'

@description('Azure OpenAI API Key (optional)')
@secure()
param azureApiKey string = ''

@description('Azure OpenAI Endpoint (optional)')
param azureApiBase string = ''

@description('Anthropic API Key (optional)')
@secure()
param anthropicApiKey string = ''

@description('Enable verbose logging')
param verboseLogging bool = true

var environmentVariables = [
  {
    name: 'OPENAI_API_KEY'
    secureValue: openaiApiKey
  }
  {
    name: 'DEFAULT_MODEL'
    value: defaultModel
  }
  {
    name: 'LITELLM_VERBOSE'
    value: string(verboseLogging)
  }
  {
    name: 'AZURE_API_KEY'
    secureValue: azureApiKey
  }
  {
    name: 'AZURE_API_BASE'
    value: azureApiBase
  }
  {
    name: 'ANTHROPIC_API_KEY'
    secureValue: anthropicApiKey
  }
]

resource containerGroup 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: containerName
  location: location
  properties: {
    containers: [
      {
        name: containerName
        properties: {
          image: containerImage
          ports: [
            {
              port: 8080
              protocol: 'TCP'
            }
          ]
          environmentVariables: environmentVariables
          resources: {
            requests: {
              cpu: cpuCores
              memoryInGB: memoryInGb
            }
          }
        }
      }
    ]
    osType: 'Linux'
    restartPolicy: 'Always'
    ipAddress: {
      type: 'Public'
      ports: [
        {
          port: 8080
          protocol: 'TCP'
        }
      ]
      dnsNameLabel: '${containerName}-${uniqueString(resourceGroup().id)}'
    }
  }
}

output containerFQDN string = containerGroup.properties.ipAddress.fqdn
output containerIP string = containerGroup.properties.ipAddress.ip
output containerURL string = 'http://${containerGroup.properties.ipAddress.fqdn}:8080'