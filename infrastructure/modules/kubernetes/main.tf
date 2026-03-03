# Kubernetes Module
#
# This module creates Kubernetes resources and installs essential controllers:
# - Platform Configuration ConfigMap
# - GP3 Storage Class (default)
# - External Secrets Operator (via Helm)
# - AWS Load Balancer Controller (via Helm)
#
# Resources are organized across multiple files:
# - configmap.tf: Platform configuration ConfigMap
# - storage.tf: Storage class resources
# - external-secrets.tf: External Secrets Operator Helm chart
# - load-balancer-controller.tf: AWS Load Balancer Controller Helm chart
#
# It requires the Kubernetes and Helm providers to be configured by the calling module.

terraform {
  required_version = ">= 1.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.0"
    }
  }
}
