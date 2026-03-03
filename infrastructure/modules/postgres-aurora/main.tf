# PostgreSQL Aurora Module
#
# This module creates a production-ready Amazon Aurora PostgreSQL cluster with:
# - Aurora PostgreSQL 16.6 cluster with 2 instances
# - Secrets Manager integration for password management
# - IAM database authentication support
# - KMS encryption for data at rest (configurable)
# - Enhanced monitoring with CloudWatch logs
# - Automated backups with AWS Backup
# - SNS notifications for RDS events
# - Security groups with least-privilege access
# - Parameter groups optimized for PostgreSQL
#
# The cluster is deployed in private subnets for security and includes
# comprehensive monitoring, backup, and notification capabilities.

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
