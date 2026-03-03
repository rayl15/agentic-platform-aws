# ElastiCache Redis Module
#
# This module creates a configurable Redis ElastiCache cluster that can be used
# for various caching purposes. The cache name and purpose are configurable,
# allowing the same module to be reused for different cache instances.
#
# Use cases include:
# - Rate limiting and throttling
# - Session storage and management
# - Application caching and temporary data
# - Message queuing and pub/sub
# - Real-time analytics and counters
#
# Features:
# - Redis 7.0 with automatic failover and multi-AZ deployment
# - Encryption at rest and in transit
# - Secrets Manager integration for authentication
# - Parameter group for Redis optimization
# - Security group with VPC-only access
# - Configurable node type and cluster size
# - Automated backups and maintenance windows
# - Configurable cache naming for multiple instances
#
# The cluster is deployed in private subnets for security and includes
# comprehensive monitoring and backup capabilities.

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.0"
    }
  }
}

# Get current region and account data
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
