# Launch template for EKS nodes with IMDSv2 and encryption
resource "aws_launch_template" "eks_nodes" {
  # checkov:skip=CKV_AWS_341: "hop limit needs to be 2 in a container environment w/ IMDSv2 enabled. See: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html#imds-considerations"
  name = "${var.name_prefix}eks-node-template"

  # Enable IMDSv2
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"  # Require IMDSv2
    http_put_response_hop_limit = 2
  }

  # Enable EBS encryption
  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size           = 20
      volume_type           = "gp3"
      delete_on_termination = true
      encrypted             = true
      kms_key_id            = var.enable_kms_encryption ? var.kms_key_arn : null
    }
  }

  # Use the EKS node security group
  vpc_security_group_ids = [aws_security_group.eks_nodes_sg.id]

  tag_specifications {
    resource_type = "instance"
    tags = merge(
      var.common_tags,
      {
        Name = "${var.name_prefix}eks-node"
      }
    )
  }

  tags = var.common_tags
}

# EKS Node Group
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.name_prefix}node-group"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = var.private_subnet_ids
  
  # Use t3.medium for a small cluster
  instance_types = ["t3.medium"]
  
  scaling_config {
    desired_size = 4
    max_size     = 6
    min_size     = 2
  }

  # Enable node group update config
  update_config {
    max_unavailable = 1
  }

  # Use launch template for additional security configurations
  launch_template {
    id      = aws_launch_template.eks_nodes.id
    version = aws_launch_template.eks_nodes.latest_version
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy,
    aws_eks_addon.vpc_cni,
    aws_eks_addon.kube_proxy
  ]

  tags = var.common_tags
}
