# LiteLLM Module
#
# This module creates LiteLLM resources including secrets management
# and configuration for the AI model proxy service.

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
