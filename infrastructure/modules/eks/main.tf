# EKS Module
#
# This module creates a complete Amazon EKS cluster with:
# - EKS cluster with private endpoint access
# - Managed node groups with launch templates
# - Required EKS addons (VPC CNI, CoreDNS, kube-proxy, EBS CSI, ADOT, cert-manager)
# - IAM roles and policies for cluster and nodes
# - Security groups with proper ingress/egress rules
# - CloudWatch logging for control plane
# - Access entries for modern EKS authentication
# - KMS encryption support for secrets and EBS volumes
#
# The cluster is configured for production workloads with:
# - Private subnets only for enhanced security
# - IMDSv2 enforcement on worker nodes
# - EBS encryption with optional KMS keys
# - Comprehensive logging and monitoring
# - IRSA (IAM Roles for Service Accounts) support

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
