# Networking Module
#
# This module creates a complete VPC setup including:
# - VPC with DNS support
# - Public and private subnets across 2 AZs
# - Internet Gateway and NAT Gateways
# - Route tables and associations
# - VPC Flow Logs with CloudWatch integration
# - Proper security group defaults
#
# The module is designed for EKS workloads with appropriate
# Kubernetes tags for load balancer integration.

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}
