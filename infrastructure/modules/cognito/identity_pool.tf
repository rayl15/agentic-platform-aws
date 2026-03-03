########################################################
# Cognito Identity Pool
########################################################

resource "aws_cognito_identity_pool" "main" {
  count = var.enable_federated_identity ? 1 : 0
  
  identity_pool_name               = "${var.name_prefix}identity-pool"
  allow_unauthenticated_identities = false
  
  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.web_client.id
    provider_name           = "cognito-idp.${local.aws_region}.amazonaws.com/${aws_cognito_user_pool.main.id}"
    server_side_token_check = false
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}identity-pool"
    }
  )
}

########################################################
# IAM Roles for Identity Pool
########################################################

resource "aws_iam_role" "authenticated" {
  count = var.enable_federated_identity ? 1 : 0
  
  name = "${var.name_prefix}cognito-authenticated"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "cognito-identity.amazonaws.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "cognito-identity.amazonaws.com:aud" = aws_cognito_identity_pool.main[0].id
          }
          "ForAnyValue:StringLike" = {
            "cognito-identity.amazonaws.com:amr" = "authenticated"
          }
        }
      }
    ]
  })
  
  tags = var.common_tags
}

# Basic permissions for authenticated users
resource "aws_iam_role_policy" "authenticated" {
  count = var.enable_federated_identity ? 1 : 0
  
  name = "${var.name_prefix}authenticated-policy"
  role = aws_iam_role.authenticated[0].id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "mobileanalytics:PutEvents"
        ]
        Resource = "*"
        Condition = {
          "StringLike": {
            "mobileanalytics:app-id": var.use_custom_domain ? [
              "com.${var.domain_name}.*",
              "${var.environment}.${var.domain_name}.*"
            ] : [
              "${var.name_prefix}*",
              "${var.environment}-${local.suffix}*"
            ]
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "cognito-sync:ListRecords",
          "cognito-sync:GetIdentityPoolConfiguration",
          "cognito-sync:GetDataset"
        ]
        Resource = [
          "arn:aws:cognito-sync:${local.aws_region}:${data.aws_caller_identity.current.account_id}:identitypool/${aws_cognito_identity_pool.main[0].id}/identity/*/dataset/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "cognito-sync:UpdateRecords",
          "cognito-sync:RefreshDataset",
          "cognito-sync:DescribeDataset",
          "cognito-sync:DeleteDataset"
        ]
        Resource = [
          "arn:aws:cognito-sync:${local.aws_region}:${data.aws_caller_identity.current.account_id}:identitypool/${aws_cognito_identity_pool.main[0].id}/identity/*/dataset/*"
        ]
        Condition = {
          "StringEquals": {
            "cognito-identity.amazonaws.com:sub": ["${data.aws_caller_identity.current.user_id}"]
          }
        }
      }
    ]
  })
}

# Connect the Identity Pool with the IAM roles
resource "aws_cognito_identity_pool_roles_attachment" "main" {
  count = var.enable_federated_identity ? 1 : 0
  
  identity_pool_id = aws_cognito_identity_pool.main[0].id
  
  roles = {
    "authenticated" = aws_iam_role.authenticated[0].arn
  }
}
