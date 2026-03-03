# EKS Cluster Security Group
resource "aws_security_group" "eks_cluster_sg" {
  # checkov:skip=CKV_AWS_382: "EKS cluster requires outbound access for AWS API communication"
  name        = "${var.name_prefix}eks-cluster-sg"
  description = "Security group for EKS cluster control plane"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}eks-cluster-sg"
    }
  )
}

# EKS Node Security Group
resource "aws_security_group" "eks_nodes_sg" {
  # checkov:skip=CKV_AWS_382: "EKS nodes require outbound access for container images and updates"
  name        = "${var.name_prefix}eks-nodes-sg"
  description = "Security group for EKS worker nodes"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}eks-nodes-sg"
    }
  )
}

# Allow worker nodes to communicate with the cluster
resource "aws_security_group_rule" "nodes_to_cluster" {
  description              = "Allow worker nodes to communicate with the cluster API Server"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.eks_cluster_sg.id
  source_security_group_id = aws_security_group.eks_nodes_sg.id
  to_port                  = 443
  type                     = "ingress"
}

# Allow cluster to communicate with worker nodes
resource "aws_security_group_rule" "cluster_to_nodes" {
  description              = "Allow cluster API Server to communicate with the worker nodes"
  from_port                = 1025
  protocol                 = "tcp"
  security_group_id        = aws_security_group.eks_nodes_sg.id
  source_security_group_id = aws_security_group.eks_cluster_sg.id
  to_port                  = 65535
  type                     = "ingress"
}

# Allow cluster to communicate with worker nodes on kubelet port
resource "aws_security_group_rule" "cluster_to_nodes_kubelet" {
  description              = "Allow cluster API Server to communicate with kubelet on worker nodes"
  from_port                = 10250
  protocol                 = "tcp"
  security_group_id        = aws_security_group.eks_nodes_sg.id
  source_security_group_id = aws_security_group.eks_cluster_sg.id
  to_port                  = 10250
  type                     = "ingress"
}

# Allow worker nodes to communicate with each other
resource "aws_security_group_rule" "nodes_to_nodes" {
  description              = "Allow worker nodes to communicate with each other"
  from_port                = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.eks_nodes_sg.id
  source_security_group_id = aws_security_group.eks_nodes_sg.id
  to_port                  = 65535
  type                     = "ingress"
}

########################################################
# Bastion Host Access Rules
########################################################

# Allow bastion instance to communicate with the EKS API server
resource "aws_security_group_rule" "bastion_to_cluster" {
  count                    = length(var.bastion_security_group_ids)
  description              = "Allow bastion instance to communicate with the cluster API Server"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.eks_cluster_sg.id
  source_security_group_id = var.bastion_security_group_ids[count.index]
  to_port                  = 443
  type                     = "ingress"
}

# Allow cluster to communicate with the bastion instance
resource "aws_security_group_rule" "cluster_to_bastion" {
  count                    = length(var.bastion_security_group_ids)
  description              = "Allow cluster API Server to communicate with the bastion instance"
  from_port                = 1024
  protocol                 = "tcp"
  security_group_id        = var.bastion_security_group_ids[count.index]
  source_security_group_id = aws_security_group.eks_cluster_sg.id
  to_port                  = 65535
  type                     = "ingress"
}
