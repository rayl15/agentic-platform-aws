# IRSA for External Secrets Operator - Secret management
resource "aws_iam_policy" "external_secrets_policy" {
  name        = "${var.name_prefix}external-secrets-policy"
  description = "Policy to allow External Secrets Operator to access Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = length(var.secrets_manager_arns) > 0 ? var.secrets_manager_arns : ["*"]
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_policy" "external_secrets_parameter_store_policy" {
  name        = "${var.name_prefix}external-secrets-parameter-store-policy"
  description = "Policy to allow External Secrets Operator to read from Parameter Store"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = length(var.parameter_store_arns) > 0 ? var.parameter_store_arns : [
          "arn:aws:ssm:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:parameter/${var.name_prefix}*"
        ]
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_role" "external_secrets_role" {
  name = "${var.name_prefix}external-secrets-role"

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
            "${replace(var.cluster_oidc_issuer_url, "https://", "")}:sub": "system:serviceaccount:external-secrets-system:external-secrets"
          }
        }
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_role_policy_attachment" "external_secrets_attachment" {
  policy_arn = aws_iam_policy.external_secrets_policy.arn
  role       = aws_iam_role.external_secrets_role.name
}

resource "aws_iam_role_policy_attachment" "external_secrets_parameter_store_attachment" {
  policy_arn = aws_iam_policy.external_secrets_parameter_store_policy.arn
  role       = aws_iam_role.external_secrets_role.name
}
