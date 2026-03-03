# IRSA for OpenTelemetry Collector - Observability data shipping
resource "aws_iam_policy" "otel_opensearch_policy" {
  name        = "${var.name_prefix}otel-opensearch-policy"
  description = "Policy to allow OpenTelemetry collector to access OpenSearch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "es:ESHttpPost",
          "es:ESHttpPut",
          "es:ESHttpGet"
        ]
        Resource = var.opensearch_domain_arn != null ? "${var.opensearch_domain_arn}/*" : "*"
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_role" "otel_collector_role" {
  name = "${var.name_prefix}otel-collector-role"

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
            "${replace(var.cluster_oidc_issuer_url, "https://", "")}:sub": "system:serviceaccount:opentelemetry-operator-system:opentelemetry-operator-controller-manager"
          }
        }
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_role_policy_attachment" "otel_opensearch_attachment" {
  policy_arn = aws_iam_policy.otel_opensearch_policy.arn
  role       = aws_iam_role.otel_collector_role.name
}
