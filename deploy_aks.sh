#!/bin/bash
# deploy_aks.sh
set -e

RG="Sprint1-Terraform"
LOCATION="eastus"

# 1. Provision Infrastructure
echo "Provisioning AKS Infrastructure..."
terraform init
terraform apply -auto-approve

# 2. Get ACR and AKS details
ACR_NAME=$(terraform output -raw acr_login_server | cut -d. -f1)
ACR_LOGIN_SERVER=$(terraform output -raw acr_login_server)
AKS_CLUSTER=$(terraform output -raw aks_cluster_name)

# 3. Build and Push Image to ACR
echo "Building and Pushing Image to $ACR_LOGIN_SERVER..."
az acr build --registry $ACR_NAME --image litellm:latest --file dockerfile .

# 4. Get AKS Credentials
echo "Getting AKS Credentials..."
az aks get-credentials --resource-group $RG --name $AKS_CLUSTER --overwrite-existing

# 5. Populate Secrets from Terraform/Env
echo "Applying Secrets..."
# Use values from terraform outputs or environment
OPENAI_KEY=$(terraform output -raw openai_key)
OPENAI_ENDPOINT=$(terraform output -raw openai_endpoint)

cat <<EOF > aks/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: litellm-secrets
  namespace: default
type: Opaque
stringData:
  AZURE_API_KEY: "$OPENAI_KEY"
  AZURE_API_BASE: "$OPENAI_ENDPOINT"
  AZURE_API_VERSION: "2024-02-15-preview"
  AZURE_FOUNDRY_API_KEY: "$OPENAI_KEY"
  AZURE_FOUNDRY_API_BASE: "$OPENAI_ENDPOINT"
  AZURE_FOUNDRY_API_VERSION: "2024-02-15-preview"
  AZURE_GPT4_DEPLOYMENT: "gpt-4"
  AZURE_GPT5_DEPLOYMENT: "gpt-35-turbo"
EOF
kubectl apply -f aks/secret.yaml

# 6. Deploy Application
echo "Deploying LiteLLM Gateway..."
sed "s|<ACR_LOGIN_SERVER>|$ACR_LOGIN_SERVER|g" aks/manifests.yaml | kubectl apply -f -

echo "Waiting for LoadBalancer IP..."
kubectl wait --for=condition=ready pod -l app=litellm-gateway --timeout=120s
LB_IP=""
while [ -z "$LB_IP" ]; do
  LB_IP=$(kubectl get svc litellm-gateway -n default -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
  [ -z "$LB_IP" ] && sleep 5
done

echo "Deployment Complete!"
echo "Gateway URL: http://$LB_IP"
