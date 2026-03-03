# Bastion Host Module
#
# This module creates a bastion host (jump server) for secure access to VPC-internal resources.
# The bastion includes:
# - EC2 instance in private subnet with Systems Manager access
# - IAM roles and policies for EKS, RDS, Bedrock, and other AWS services
# - Pre-installed development tools (kubectl, AWS CLI, code-server, etc.)
# - Security groups with minimal required access
#
# The bastion is designed for development and deployment activities within the VPC,
# providing secure access to internal resources like EKS clusters and RDS databases.

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
