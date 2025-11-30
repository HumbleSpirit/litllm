# LiteLLM Azure OpenAI Gateway

FastAPI-based gateway for routing LLM requests to Azure OpenAI, with support for multiple providers.

## Features

- 🚀 **Azure OpenAI Integration**: Direct routing to Azure-hosted GPT-4 and GPT-3.5 models
- 🌐 **Multi-Provider Support**: OpenAI, Anthropic, Azure (via LiteLLM)
- 🐳 **Docker Ready**: Containerized for easy deployment
- ☁️ **Azure Deployment**: Automated scripts for Azure App Service
- 🎨 **Web UI**: Simple chat interface for testing

## Quick Start

### 1. Setup Azure Resources

```bash
./setup_azure_resources.sh
```

This creates:

- Azure Resource Group
- Azure OpenAI resource with GPT-4 and GPT-3.5 deployments
- Azure Container Registry
- Azure App Service (Web App)

### 2. Local Development

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your Azure keys

# Run with Docker
docker build -t litellm-gateway .
docker run -d -p 8080:8080 --env-file .env litellm-gateway
```

Access at `http://localhost:8080`

### 3. Update Deployment

```bash
./update_azure.sh
```

### 4. Infrastructure as Code (IaC)

**Bicep:**

```bash
# Create resource group first
az group create --name Sprint1-Fresh --location eastus

# Deploy infrastructure
az deployment group create \
  --resource-group Sprint1-Fresh \
  --template-file main.bicep

# Note: You'll still need to build and push the Docker image to ACR
# and configure the Web App to use it
```

**Terraform:**

```bash
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Apply infrastructure
terraform apply

# Note: You'll still need to build and push the Docker image to ACR
# and configure the Web App to use it
```

## Configuration

### Required Environment Variables

```bash
# Azure OpenAI
AZURE_FOUNDRY_API_KEY=<your-key>
AZURE_FOUNDRY_API_BASE=https://<resource>.openai.azure.com/
AZURE_FOUNDRY_API_VERSION=2024-02-15-preview
AZURE_GPT4_DEPLOYMENT=gpt-4
AZURE_GPT5_DEPLOYMENT=gpt-35-turbo
```

### Optional Providers

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## API Endpoints

- `GET /` - Web UI
- `POST /v1/chat` - Simple chat endpoint
- `POST /v1/chat/completions` - OpenAI-compatible endpoint
- `GET /v1/models` - List available models
- `GET /health` - Health check

## Architecture

```text
User Request → FastAPI → LiteLLM → Azure OpenAI
                                 → OpenAI
                                 → Anthropic
```

## Troubleshooting

### 401 Unauthorized

- Verify `AZURE_FOUNDRY_API_BASE` matches your resource endpoint
- Ensure API key is exactly 32 characters (standard Azure OpenAI key)
- Check that `AZURE_FOUNDRY_API_BASE` does NOT use `.services.ai.azure.com` (that's for AI Studio projects)

### 404 Deployment Not Found

- Verify deployment names match: `AZURE_GPT4_DEPLOYMENT=gpt-4`
- Check deployments exist: `az cognitiveservices account deployment list --name <resource> --resource-group <rg>`

### Model Version Deprecated

- Use `gpt-4o:2024-11-20` instead of `gpt-4:turbo-2024-04-09`
- Use `gpt-4o-mini:2024-07-18` instead of `gpt-35-turbo:0125`

## Scripts

- `setup_azure_resources.sh` - Full Azure setup from scratch
- `update_azure.sh` - Update existing deployment
- `deploy_azure.sh` - Deploy to new resource group (destructive)
- `verify_azure_keys.py` - Test Azure credentials

## License

MIT
