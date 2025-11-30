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

variable "resource_group_name" {
  default = "Sprint1-Fresh"
}

variable "location" {
  default = "eastus"
}

variable "openai_name" {
  default = "litellm-openai"
}

variable "acr_name" {
  default = "litellmacr"
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# Azure OpenAI Resource
resource "azurerm_cognitive_account" "openai" {
  name                = "${var.openai_name}-${random_string.suffix.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "OpenAI"
  sku_name            = "S0"

  custom_subdomain_name = "${var.openai_name}-${random_string.suffix.result}"
}

# Random suffix for unique names
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# GPT-4 Deployment (using gpt-4o)
resource "azurerm_cognitive_deployment" "gpt4" {
  name                 = "gpt-4"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-11-20"
  }

  sku {
    name     = "Standard"
    capacity = 10
  }
}

# GPT-3.5 Deployment (using gpt-4o-mini)
resource "azurerm_cognitive_deployment" "gpt35" {
  name                 = "gpt-35-turbo"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o-mini"
    version = "2024-07-18"
  }

  sku {
    name     = "GlobalStandard"
    capacity = 10
  }

  depends_on = [azurerm_cognitive_deployment.gpt4]
}

# Container Registry
resource "azurerm_container_registry" "acr" {
  name                = "${var.acr_name}${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Standard"
  admin_enabled       = true
}

# App Service Plan
resource "azurerm_service_plan" "plan" {
  name                = "litellm-plan"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "B1"
}

# Web App
resource "azurerm_linux_web_app" "app" {
  name                = "litellm-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.plan.id

  site_config {
    application_stack {
      docker_image_name        = "litellm:latest"
      docker_registry_url      = "https://${azurerm_container_registry.acr.login_server}"
      docker_registry_username = azurerm_container_registry.acr.admin_username
      docker_registry_password = azurerm_container_registry.acr.admin_password
    }
  }

  app_settings = {
    "WEBSITES_PORT"             = "8080"
    "LITELLM_VERBOSE"           = "True"
    "DEFAULT_MODEL"             = "azure/gpt-4"
    "AZURE_API_KEY"             = azurerm_cognitive_account.openai.primary_access_key
    "AZURE_API_BASE"            = azurerm_cognitive_account.openai.endpoint
    "AZURE_API_VERSION"         = "2024-02-15-preview"
    "AZURE_FOUNDRY_API_KEY"     = azurerm_cognitive_account.openai.primary_access_key
    "AZURE_FOUNDRY_API_BASE"    = azurerm_cognitive_account.openai.endpoint
    "AZURE_FOUNDRY_API_VERSION" = "2024-02-15-preview"
    "AZURE_GPT4_DEPLOYMENT"     = "gpt-4"
    "AZURE_GPT5_DEPLOYMENT"     = "gpt-35-turbo"
  }
}

# Outputs
output "openai_endpoint" {
  value = azurerm_cognitive_account.openai.endpoint
}

output "openai_key" {
  value     = azurerm_cognitive_account.openai.primary_access_key
  sensitive = true
}

output "web_app_url" {
  value = "https://${azurerm_linux_web_app.app.default_hostname}"
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}
