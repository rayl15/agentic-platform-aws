#!/bin/bash

set -e  # Exit on any error

echo "========================================="
echo "Deploying LiteLLM"
echo "========================================="

# Deploy LiteLLM with Helm
echo "Deploying LiteLLM to Kubernetes with Helm..."
helm upgrade --install litellm ./k8s/helm/charts/litellm

echo "Deployment complete!"

echo "========================================="
echo "✅ LiteLLM deployment completed!"
echo "========================================="

# Check the deployment status
echo "Checking deployment status..."
kubectl get pods -l app=litellm -n default
echo ""

# Check if external secret exists and is synced
echo "Checking external secret status..."
kubectl get externalsecret litellm-secret -n default -o wide 2>/dev/null || echo "External secret not found"
echo ""

# Check if the secret was created
echo "Checking if litellm-secret exists..."
kubectl get secret litellm-secret -n default 2>/dev/null || echo "Secret not found - external secret may still be syncing"
echo ""

# Check service account
echo "Checking service account..."
kubectl get serviceaccount litellm-sa -n default -o yaml
echo ""

echo "========================================="
echo "✅ LiteLLM deployment status check completed!"
echo "========================================="
