# IRSA for Agent Role - General agent service account
resource "aws_iam_role" "agent_role" {
  name = "${var.name_prefix}agent-role"

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
            "${replace(var.cluster_oidc_issuer_url, "https://", "")}:aud": "sts.amazonaws.com"
          }
          StringLike = {
            "${replace(var.cluster_oidc_issuer_url, "https://", "")}:sub": "system:serviceaccount:default:*agent-sa"
          }
        }
      }
    ]
  })

  tags = var.common_tags
}

# Policy to allow agents to read agent secret for authentication
resource "aws_iam_policy" "agent_secret_policy" {
  count = length(var.agent_secret_arns) > 0 ? 1 : 0
  
  name        = "${var.name_prefix}agent-secret-policy"
  description = "Policy to allow agents to read agent secret for authentication"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = var.agent_secret_arns
      }
    ]
  })

  tags = var.common_tags
}

# Attach the agent secret policy to the agent role
resource "aws_iam_role_policy_attachment" "agent_secret_attachment" {
  count = length(aws_iam_policy.agent_secret_policy) > 0 ? 1 : 0
  
  role       = aws_iam_role.agent_role.name
  policy_arn = aws_iam_policy.agent_secret_policy[0].arn
}
