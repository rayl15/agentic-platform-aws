# IRSA for LiteLLM - AI model proxy with Bedrock, PostgreSQL, and Redis access
resource "aws_iam_policy" "litellm_bedrock_policy" {
  name        = "${var.name_prefix}litellm-bedrock-policy"
  description = "Policy to allow LiteLLM to invoke Bedrock models"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          # Allow access to all models in the account across all regions
          "arn:aws:bedrock:*:${data.aws_caller_identity.current.account_id}:model/*",
          # Allow access to all inference profiles in the account across all regions
          "arn:aws:bedrock:*:${data.aws_caller_identity.current.account_id}:inference-profile/*",
          # Allow access to AWS foundation models
          "arn:aws:bedrock:*::foundation-model/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:ListFoundationModels",
          "bedrock:GetFoundationModel"
        ]
        Resource = [
          # These are read-only list operations that require * resource
          # but we're scoping them to only foundation model related actions
          "arn:aws:bedrock:*:${data.aws_caller_identity.current.account_id}:*"
        ]
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_policy" "litellm_secrets_policy" {
  count = length(var.litellm_secret_arns) > 0 || length(var.redis_secret_arns) > 0 ? 1 : 0
  
  name        = "${var.name_prefix}litellm-secrets-policy"
  description = "Policy to allow LiteLLM to access its secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = concat(
          var.litellm_secret_arns,
          var.redis_secret_arns
        )
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_policy" "litellm_postgres_policy" {
  count = length(var.litellm_postgres_db_user_arns) > 0 ? 1 : 0
  
  name        = "${var.name_prefix}litellm-postgres-policy"
  description = "Policy to allow LiteLLM to access PostgreSQL"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Allow RDS IAM authentication
      {
        Effect = "Allow"
        Action = [
          "rds-db:connect"
        ]
        Resource = var.litellm_postgres_db_user_arns
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_policy" "litellm_redis_policy" {
  count = length(var.redis_cluster_arns) > 0 || length(var.redis_secret_arns) > 0 ? 1 : 0
  
  name        = "${var.name_prefix}litellm-redis-policy"
  description = "Policy to allow LiteLLM to access Redis cluster"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "elasticache:Connect",
          "secretsmanager:GetSecretValue"
        ],
        Resource = concat(
          var.redis_cluster_arns,
          var.redis_secret_arns
        )
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_role" "litellm_role" {
  name = "${var.name_prefix}litellm-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/${replace(var.cluster_oidc_issuer_url, "https://", "")}"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${replace(var.cluster_oidc_issuer_url, "https://", "")}:sub": "system:serviceaccount:default:litellm-sa"
          }
        }
      }
    ]
  })

  tags = var.common_tags
}

# Attach policies to the LiteLLM role
resource "aws_iam_role_policy_attachment" "litellm_bedrock_attachment" {
  policy_arn = aws_iam_policy.litellm_bedrock_policy.arn
  role       = aws_iam_role.litellm_role.name
}

resource "aws_iam_role_policy_attachment" "litellm_secrets_attachment" {
  count = length(aws_iam_policy.litellm_secrets_policy) > 0 ? 1 : 0
  
  policy_arn = aws_iam_policy.litellm_secrets_policy[0].arn
  role       = aws_iam_role.litellm_role.name
}

resource "aws_iam_role_policy_attachment" "litellm_postgres_attachment" {
  count = length(aws_iam_policy.litellm_postgres_policy) > 0 ? 1 : 0
  
  policy_arn = aws_iam_policy.litellm_postgres_policy[0].arn
  role       = aws_iam_role.litellm_role.name
}

resource "aws_iam_role_policy_attachment" "litellm_redis_attachment" {
  count = length(aws_iam_policy.litellm_redis_policy) > 0 ? 1 : 0
  
  policy_arn = aws_iam_policy.litellm_redis_policy[0].arn
  role       = aws_iam_role.litellm_role.name
}
