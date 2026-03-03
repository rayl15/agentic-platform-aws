# IAM policy to allow connection to Redis cluster and access auth token
resource "aws_iam_policy" "redis_cache_connect" {
  name        = "${var.name_prefix}${var.cache_name}-connect"
  description = "Policy to allow connection to platform Redis cache cluster and access auth token"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.redis_cache_auth.arn
        ]
      }
    ]
  })

  tags = var.common_tags
}
