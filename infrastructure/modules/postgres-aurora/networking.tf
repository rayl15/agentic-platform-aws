# Subnet group for the cluster
resource "aws_db_subnet_group" "postgres" {
  name       = "${var.name_prefix}postgres"
  subnet_ids = var.private_subnet_ids

  tags = var.common_tags
}

# Security group for the cluster
resource "aws_security_group" "postgres" {
  name_prefix = "${var.name_prefix}postgres-"
  vpc_id      = var.vpc_id
  description = "Security group for PostgreSQL database"

  tags = var.common_tags

  lifecycle {
    create_before_destroy = true
  }
}

# Ingress rule - Allow from EKS nodes security group
resource "aws_security_group_rule" "postgres_ingress_eks_nodes" {
  count = length(var.eks_node_security_group_ids)
  
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  security_group_id = aws_security_group.postgres.id
  source_security_group_id = var.eks_node_security_group_ids[count.index]
  description       = "Allow PostgreSQL traffic from EKS nodes"
}

# Ingress rule - Allow from bastion security group
resource "aws_security_group_rule" "postgres_ingress_bastion" {
  count = length(var.bastion_security_group_ids)
  
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.postgres.id
  source_security_group_id = var.bastion_security_group_ids[count.index]
  description              = "Allow PostgreSQL traffic from bastion instance"
}

# Egress rule
resource "aws_security_group_rule" "postgres_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.postgres.id
  cidr_blocks       = [var.vpc_cidr_block]
  description       = "Allow outbound traffic only within the VPC"
}
