# OIDC Provider for EKS
#
# This creates the IAM OIDC identity provider for the EKS cluster, which is required
# for IRSA (IAM Roles for Service Accounts) functionality. This allows Kubernetes
# service accounts to assume AWS IAM roles and access AWS services securely.

# Get the TLS certificate for the EKS OIDC provider
data "tls_certificate" "eks" {
  url = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

# Create the IAM OIDC identity provider
resource "aws_iam_openid_connect_provider" "eks" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.main.identity[0].oidc[0].issuer

  tags = var.common_tags
}
