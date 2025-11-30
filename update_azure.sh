#!/bin/bash
set -e

# Configuration - using the existing Sprint1-Fresh resources
RG="Sprint1-Fresh"
ACR_NAME="litellmfresh"
WEBAPP_NAME=$(az webapp list -g $RG --query "[0].name" -o tsv)
IMAGE_NAME="litellm:latest"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Updating Azure Web App...${NC}"

# 1. Login Check
az account show > /dev/null 2>&1 || az login

# 2. Get ACR details
echo -e "${GREEN}Getting ACR details...${NC}"
ACR_LOGIN_SERVER=$(az acr show -n $ACR_NAME -g $RG --query loginServer -o tsv 2>/dev/null || echo "")

if [ -z "$ACR_LOGIN_SERVER" ]; then
    echo -e "${YELLOW}ACR not found. Creating new ACR...${NC}"
    ACR_NAME="litellmfresh$RANDOM"
    az acr create --resource-group $RG --name $ACR_NAME --sku Standard --admin-enabled true
    ACR_LOGIN_SERVER=$(az acr show -n $ACR_NAME -g $RG --query loginServer -o tsv)
fi

# 3. Build and Push Image
echo -e "${GREEN}Building and Pushing Image to ACR...${NC}"
az acr build --registry $ACR_NAME --image $IMAGE_NAME --file dockerfile .

# 4. Get Web App details
if [ -z "$WEBAPP_NAME" ]; then
    echo -e "${YELLOW}No Web App found. Creating new one...${NC}"
    APP_PLAN="litellm-plan-fresh"
    WEBAPP_NAME="litellm-fresh-$RANDOM"
    
    az appservice plan create -g $RG -n $APP_PLAN --is-linux --sku B1
    az webapp create -g $RG -p $APP_PLAN -n $WEBAPP_NAME --container-image-name "$ACR_LOGIN_SERVER/$IMAGE_NAME"
fi

# 5. Configure Web App
echo -e "${GREEN}Configuring Web App...${NC}"
ACR_USER=$(az acr credential show -n $ACR_NAME --query username -o tsv)
ACR_PASS=$(az acr credential show -n $ACR_NAME --query passwords[0].value -o tsv)

az webapp config container set -g $RG -n $WEBAPP_NAME \
  --container-image-name "$ACR_LOGIN_SERVER/$IMAGE_NAME" \
  --container-registry-url "https://$ACR_LOGIN_SERVER" \
  --container-registry-user "$ACR_USER" \
  --container-registry-password "$ACR_PASS"

# 6. Update Environment Variables
echo -e "${GREEN}Updating Environment Variables...${NC}"
ENV_VARS=""
if [ -f .env ]; then
    while IFS= read -r line || [[ -n "$line" ]]; do
        if [[ ! "$line" =~ ^# ]] && [[ -n "$line" ]]; then
            CLEAN_LINE=${line%%#*}
            CLEAN_LINE=$(echo "$CLEAN_LINE" | xargs)
            if [[ -n "$CLEAN_LINE" ]]; then
                ENV_VARS="$ENV_VARS $CLEAN_LINE"
            fi
        fi
    done < .env
fi

if [ -n "$ENV_VARS" ]; then
    az webapp config appsettings set -g $RG -n $WEBAPP_NAME --settings $ENV_VARS
fi

# 7. Restart Web App
echo -e "${GREEN}Restarting Web App...${NC}"
az webapp restart -g $RG -n $WEBAPP_NAME

# 8. Final Output
HOSTNAME=$(az webapp show -g $RG -n $WEBAPP_NAME --query defaultHostName -o tsv)
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "App URL: https://$HOSTNAME"
