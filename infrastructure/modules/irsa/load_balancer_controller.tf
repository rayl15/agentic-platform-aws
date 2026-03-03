# IRSA for AWS Load Balancer Controller
resource "aws_iam_role" "load_balancer_controller_role" {
  name = "${var.name_prefix}aws-load-balancer-controller-role"

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
            "${replace(var.cluster_oidc_issuer_url, "https://", "")}:aud": "sts.amazonaws.com",
            "${replace(var.cluster_oidc_issuer_url, "https://", "")}:sub": "system:serviceaccount:kube-system:aws-load-balancer-controller"
          }
        }
      }
    ]
  })

  # Add the required principal tag for the managed policy to work
  tags = merge(
    var.common_tags,
    {
      "eks:eks-cluster-name" = var.cluster_name
    }
  )
}

# Create the AWS Load Balancer Controller IAM policy
resource "aws_iam_policy" "load_balancer_controller_policy" {
  name        = "${var.name_prefix}aws-load-balancer-controller-policy"
  description = "IAM policy for AWS Load Balancer Controller"
  
  policy = file("${path.module}/policies/aws_load_balancer_controller_policy.json")

  tags = var.common_tags
}

# Attach the AWS Load Balancer Controller IAM policy to the role
resource "aws_iam_role_policy_attachment" "load_balancer_controller" {
  policy_arn = aws_iam_policy.load_balancer_controller_policy.arn
  role       = aws_iam_role.load_balancer_controller_role.name
}
