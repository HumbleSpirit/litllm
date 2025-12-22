# Implementation Details: LiteLLM Gateway

This document summarizes the architecture, files, and implementation steps taken to create the LiteLLM Gateway and its associated chat interface.

## 🚀 Project Overview

The LiteLLM Gateway is a wrapper around LiteLLM that serves a modern web interface for interacting with models hosted on Azure OpenAI/Foundry. It features:

- **Identity Injection**: System prompts are automatically injected to make models identify as specific versions (e.g., GPT-5.2).
- **Virtual Model Mapping**: Maps user-facing model names to internal Azure deployment names.
- **Premium Chat UI**: A responsive, modern web interface with a clean aesthetic and settings for API key management.
- **Multi-Cloud Deployment**: Support for local Docker/Kubernetes and Azure (Terraform/Bicep).

---

## 📂 File Structure & Purpose

### 1. Backend & Configuration

- **`app.py`**: The core FastAPI application. It handles:
  - Routing for the web UI and `/v1/chat/completions`.
  - Virtual model mapping (e.g., `gpt-5.2` -> `gpt-5-2`).
  - System prompt injection for model "identity".
  - Basic API key authentication.
- **`.env`**: Configuration for API keys, Azure endpoints, and gateway settings.
- **`requirements.txt`**: Python dependencies (`fastapi`, `uvicorn`, `litellm`, `pydantic`).

### 2. Frontend (Modern UI)

Located in the `static/` directory:

- **`index.html`**: The structure of the chat interface, including sidebar, chat container, and settings modal.
- **`styles.css`**: Premium styling with Inter font, glassmorphism effects, and a sleek dark-themed palette.
- **`app.js`**: Frontend logic for message handling, model selection, local storage for settings, and Markdown rendering.

### 3. Containerization

- **`Dockerfile`**: Defines the multi-stage build for the FastAPI application.
- **`.dockerignore`**: Excludes local files (like `.venv` and `.git`) from the Docker build context.
- **`build_docker.sh`**: A helper script to build the Docker image.

### 4. Local Deployment (K8s/Docker)

- **`setup_registry.sh`**: Starts a local Docker registry (useful for K8s development).
- **`finish_local_deploy.sh`**: Automates applying Kubernetes manifests to a local cluster (like k3s).
- **`k8s/`**: Contains manifests for deployment:
  - `deployment.yaml`: Defines the Pod and ReplicaSet.
  - `service.yaml`: Exposes the gateway via a ClusterIP or LoadBalancer.
  - `secret.yaml`: Stores sensitive environment variables.

### 5. Azure Deployment (IaC)

- **`main.tf` / `main.bicep`**: Infrastructure as Code for deploying Azure OpenAI and related resources.
- **`aks.tf`**: Terraform configuration for provisioning an Azure Kubernetes Service (AKS) cluster.
- **`setup_azure_resources.sh`**: Orchestrates the initial setup of Azure resources.
- **`deploy_azure.sh`**: Deploys the application specifically to Azure (e.g., Web App or AKS).
- **`update_azure.sh`**: Utility for updating existing Azure deployments.

---

## 🛠️ Implementation Steps

### Step 1: Backend Development

1. Initialized a FastAPI app with `litellm` integration.
2. Implemented a virtual model mapping dictionary to abstract Azure deployment names.
3. Added `Identity Injection` logic to ensure models respond with the requested internal version name.
4. Created a `/v1/chat` endpoint for simple use-cases and `/v1/chat/completions` for OpenAI compatibility.

### Step 2: UI Design & Implementation

1. Designed a modern layout using CSS Flexbox and Grid.
2. Implemented a "Welcome Screen" vs "Chat View" transitions.
3. Added `marked.js` for real-time Markdown rendering of AI responses.
4. Integrated a sidebar for "New Chat" and "Settings" actions.

### Step 3: Containerization & Local Registry

1. Authored a Dockerfile optimized for Python/FastAPI.
2. Created `setup_registry.sh` to allow pushing images to a local development registry (`localhost:5000`).
3. Verified local execution using `docker run`.

### Step 4: Infrastructure Automation

1. Developed Terraform and Bicep templates for idempotent resource creation on Azure.
2. Created shell scripts to automate the interaction between the local environment and Azure CLI/Terraform.

### Step 5: Kubernetes Manifests

1. Wrote Kubernetes Deployment and Service manifests.
2. Created a script (`finish_local_deploy.sh`) to simplify the application of these manifests.

---

## 🔧 How to Run

### Locally with Docker

```bash
./build_docker.sh
docker run -p 8080:8080 --env-file .env litellm-gateway:latest
```

### Locally with Kubernetes (k3s)

1. Ensure your registry is up: `./setup_registry.sh`
2. Tag and push your image.
3. Run: `./finish_local_deploy.sh`

### On Azure

1. Configure your credentials in `.env`.
2. Run: `./setup_azure_resources.sh`
3. Run: `./deploy_azure.sh`
