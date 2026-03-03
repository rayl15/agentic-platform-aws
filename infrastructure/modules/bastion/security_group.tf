# Security group for the bastion instance
resource "aws_security_group" "bastion_sg" {
  # checkov:skip=CKV_AWS_382: "Bastion instance requires outbound access for AWS API communication and package updates"
  name        = "${var.name_prefix}bastion-sg"
  description = "Security group for EKS bastion instance"
  vpc_id      = var.vpc_id

  # Allow all outbound traffic
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
      Name = "${var.name_prefix}bastion-sg"
    }
  )
}
