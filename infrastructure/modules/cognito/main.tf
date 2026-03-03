# Cognito Module
#
# This module creates AWS Cognito resources for user authentication and authorization
# including user pools, identity pools, and associated IAM roles.

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Random suffix for unique resource naming
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# Local values
locals {
  suffix = random_string.suffix.result
  aws_region = data.aws_region.current.name
}
