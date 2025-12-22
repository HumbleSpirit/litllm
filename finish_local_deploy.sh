#!/bin/bash
# finish_local_deploy.sh
# Run this script on your VM to complete the deployment to 192.168.178.130

# 1. Update your ~/.kube/config to point to the correct server IP
# (Ensure the k3s.yaml you copied has server: https://192.168.178.130:6443)

# 2. Apply the manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

echo "Deploying complete. Check status with: kubectl get pods"
