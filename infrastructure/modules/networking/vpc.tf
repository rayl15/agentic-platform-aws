// AWS VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}vpc"
    }
  )
}

// Configure default security group to deny all traffic
resource "aws_default_security_group" "default" {
  vpc_id = aws_vpc.main.id

  // Empty ingress and egress blocks means no traffic is allowed
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}default-sg"
    }
  )
}

// Internet Gateway for public subnets
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}igw"
    }
  )
}

// Get current region data
data "aws_region" "current" {}
