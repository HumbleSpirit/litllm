#!/bin/bash
set -e

echo "Building and pushing Docker image to ACR..."

# Get outputs from Terraform
ACR_NAME=$(terraform output -raw acr_login_server | cut -d'.' -f1)
WEBAPP_URL=$(terraform output -raw web_app_url)
WEBAPP_NAME=$(echo $WEBAPP_URL | cut -d'/' -f3 | cut -d'.' -f1)
RG="Sprint1-Terraform"

echo "ACR: $ACR_NAME"
echo "Web App: $WEBAPP_NAME"

# Build and push image
echo "Building image..."
az acr build --registry $ACR_NAME --image litellm:latest --file dockerfile .

# Restart web app
echo "Restarting web app..."
az webapp restart --name $WEBAPP_NAME --resource-group $RG

echo "Done! Your app should be available at: $WEBAPP_URL"
