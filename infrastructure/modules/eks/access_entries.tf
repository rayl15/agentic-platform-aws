# Create EKS access entries for cluster access with access policies instead of system groups
resource "aws_eks_access_entry" "cluster_admin" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = aws_iam_role.eks_cluster_role.arn
  
  depends_on = [aws_eks_cluster.main]
}

# Associate the cluster-admin access policy with the cluster role
resource "aws_eks_access_policy_association" "cluster_admin_policy" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = aws_iam_role.eks_cluster_role.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
  
  # Add access scope block for cluster-wide access
  access_scope {
    type       = "cluster"
    namespaces = []  # Empty for cluster-wide access
  }
  
  depends_on = [aws_eks_access_entry.cluster_admin]
}

# Access entry for additional admin roles (if provided)
resource "aws_eks_access_entry" "additional_admins" {
  for_each = toset(var.additional_admin_role_arns)
  
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = each.value
  
  depends_on = [aws_eks_cluster.main]
}

# Associate the cluster-admin access policy with additional admin roles
resource "aws_eks_access_policy_association" "additional_admins_policy" {
  for_each = toset(var.additional_admin_role_arns)
  
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = each.value
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
  
  # Add access scope block for cluster-wide access
  access_scope {
    type       = "cluster"
    namespaces = []  # Empty for cluster-wide access
  }
  
  depends_on = [aws_eks_access_entry.additional_admins]
}

########################################################
# Bastion Host Access Entries
########################################################

# Access entry for bastion host IAM roles (if provided)
resource "aws_eks_access_entry" "bastion_hosts" {
  count = length(var.bastion_iam_role_arns)
  
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = var.bastion_iam_role_arns[count.index]
  
  depends_on = [aws_eks_cluster.main]
}

# Associate the cluster-admin access policy with bastion host roles
resource "aws_eks_access_policy_association" "bastion_hosts_policy" {
  count = length(var.bastion_iam_role_arns)
  
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = var.bastion_iam_role_arns[count.index]
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
  
  # Add access scope block for cluster-wide access
  access_scope {
    type       = "cluster"
    namespaces = []  # Empty for cluster-wide access
  }
  
  depends_on = [aws_eks_access_entry.bastion_hosts]
}
