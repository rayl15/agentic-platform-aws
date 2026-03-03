# KMS Module
#
# This module creates KMS encryption resources including:
# - KMS key with automatic rotation
# - Proper IAM policies for AWS services
# - KMS alias for easier reference
# - Conditional creation based on enable_kms_encryption variable
#
# The key policy allows access from:
# - Root account and specified administrators
# - CloudWatch Logs service
# - DynamoDB service

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

resource "aws_kms_key" "main" {
  count                   = var.enable_kms_encryption ? 1 : 0
  description            = "KMS key for encrypting resources in ${var.name_prefix} environment"
  deletion_window_in_days = var.kms_deletion_window
  enable_key_rotation    = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = concat(
            ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"],
            var.kms_key_administrators
          )
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt*",
          "kms:Decrypt*",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:Describe*"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow DynamoDB Service"
        Effect = "Allow"
        Principal = {
          Service = "dynamodb.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:Describe*"
        ]
        Resource = "*"
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_kms_alias" "main" {
  count         = var.enable_kms_encryption ? 1 : 0
  name          = "alias/${var.name_prefix}key"
  target_key_id = aws_kms_key.main[0].key_id
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# Get current region data
data "aws_region" "current" {}
