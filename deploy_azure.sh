#!/bin/bash
set -e

# Configuration
RG="Sprint1"
LOCATION="eastus"
ACR_NAME="litellmsprint1$RANDOM" # Adding random to ensure uniqueness if global check fails, but user asked for specific name. Let's try to stick to user's base but handle conflicts if needed. Actually user said "ACR_NAME='litellmsprint1'". I'll use that but warn if it exists.
# To ensure we can re-run, we might need to be careful. The user said "clear all previous orphan resources".
# So we will delete the RG first.
ACR_NAME="litellmsprint1" 
IMAGE_NAME="litellm:latest"
APP_PLAN="litellm-plan"
WEBAPP_NAME="litellmsprint1"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting Azure Deployment (Refactored)...${NC}"

# 1. Login Check
az account show > /dev/null 2>&1 || az login

# 2. Cleanup Orphan Resources
echo -e "${YELLOW}Cleaning up existing resources (Resource Group: $RG)...${NC}"
if [ "$(az group exists --name $RG)" = "true" ]; then
    echo "Deleting existing Resource Group $RG..."
    az group delete --name $RG --yes --no-wait
    echo "Deletion initiated. Waiting for deletion to complete (this may take a while)..."
    az group wait --deleted --name $RG
    echo "Resource Group deleted."
else
    echo "Resource Group $RG does not exist."
fi

# 3. Register Providers
echo -e "${GREEN}Registering Resource Providers...${NC}"
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.ContainerInstance
az provider register --namespace Microsoft.Web
az provider register -n Microsoft.OperationalInsights --wait

# 4. Create Resource Group & ACR
echo -e "${GREEN}Creating Resource Group & ACR...${NC}"
az group create -n $RG -l $LOCATION
az acr create --resource-group $RG --name $ACR_NAME --sku Standard --admin-enabled true

# 5. Build and Push Image
echo -e "${GREEN}Building and Pushing Image...${NC}"
ACR_LOGIN_SERVER=$(az acr show -n $ACR_NAME --query loginServer -o tsv)

# Use az acr build to build in cloud (avoids local docker issues and arch mismatches)
az acr build --registry $ACR_NAME --image $IMAGE_NAME --file dockerfile .

# 6. Create App Service Plan & Web App
echo -e "${GREEN}Creating App Service Plan & Web App...${NC}"
az appservice plan create -g $RG -n $APP_PLAN --is-linux --sku B1
az webapp create -g $RG -p $APP_PLAN -n $WEBAPP_NAME --container-image-name "$ACR_LOGIN_SERVER/$IMAGE_NAME"

# 7. Configure Web App
echo -e "${GREEN}Configuring Web App...${NC}"
ACR_USER=$(az acr credential show -n $ACR_NAME --query username -o tsv)
ACR_PASS=$(az acr credential show -n $ACR_NAME --query passwords[0].value -o tsv)

az webapp config container set -g $RG -n $WEBAPP_NAME \
  --container-image-name "$ACR_LOGIN_SERVER/$IMAGE_NAME" \
  --container-registry-url "https://$ACR_LOGIN_SERVER" \
  --container-registry-user "$ACR_USER" \
  --container-registry-password "$ACR_PASS"

# Prepare Environment Variables from .env
ENV_VARS=""
if [ -f .env ]; then
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip comments and empty lines
        if [[ ! "$line" =~ ^# ]] && [[ -n "$line" ]]; then
            # Remove inline comments (everything after #)
            CLEAN_LINE=${line%%#*}
            # Trim trailing whitespace
            CLEAN_LINE=$(echo "$CLEAN_LINE" | xargs)
            
            if [[ -n "$CLEAN_LINE" ]]; then
                ENV_VARS="$ENV_VARS $CLEAN_LINE"
            fi
        fi
    done < .env
fi

# Set App Settings
if [ -n "$ENV_VARS" ]; then
    echo "Setting environment variables..."
    az webapp config appsettings set -g $RG -n $WEBAPP_NAME --settings $ENV_VARS
fi

# 8. Final Output
HOSTNAME=$(az webapp show -g $RG -n $WEBAPP_NAME --query defaultHostName -o tsv)
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "App URL: https://$HOSTNAME"
