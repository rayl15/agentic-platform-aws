# IRSA Module
#
# This module creates IAM Roles for Service Accounts (IRSA) for the agentic platform.
# IRSA enables Kubernetes service accounts to assume IAM roles, providing secure
# access to AWS services without storing credentials in pods.
#
# The module includes roles for:
# - EBS CSI Driver (persistent volume support)
# - OpenTelemetry Collector (observability data shipping)
# - External Secrets Operator (secret management)
# - Retrieval Gateway (Bedrock Knowledge Base operations)
# - LLM Gateway (Bedrock model invocation + Redis + DynamoDB)
# - Memory Gateway (PostgreSQL access)
# - LiteLLM (AI model proxy)
# - Agent Role (general agent service account)
#
# All roles are configured to work with the EKS cluster's OIDC provider
# and follow the principle of least privilege.

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

# Get current region and account data
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
