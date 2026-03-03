# Redis Security Group
resource "aws_security_group" "redis_cache" {
  # checkov:skip=CKV_AWS_23: All security group rules have descriptions
  # checkov:skip=CKV_AWS_382: Egress is intentionally restricted to VPC CIDR only
  name        = "${var.name_prefix}${var.cache_name}-sg"
  description = "Security group for platform Redis cache cluster"
  vpc_id      = var.vpc_id

  ingress {
    description = "Redis from VPC"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_block]
  }

  egress {
    description = "Redis to VPC services only"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_block]  # Restrict to VPC CIDR only
  }

  tags = var.common_tags

  lifecycle {
    create_before_destroy = true
  }
}

# ElastiCache subnet group
resource "aws_elasticache_subnet_group" "redis_cache" {
  name       = "${var.name_prefix}${var.cache_name}"
  subnet_ids = var.private_subnet_ids
  
  tags = var.common_tags
}
