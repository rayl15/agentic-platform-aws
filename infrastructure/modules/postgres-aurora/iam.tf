# IAM role for RDS monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "${var.name_prefix}rds-monitoring"
  description = "Role for RDS enhanced monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
  
  tags = var.common_tags
}

# Add policy attachment instead of using managed_policy_arns
resource "aws_iam_role_policy_attachment" "rds_monitoring_policy" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# IAM Role for AWS Backup - simplified name
resource "aws_iam_role" "backup_role" {
  name = "${var.name_prefix}backup-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "backup.amazonaws.com"
        }
      }
    ]
  })

  tags = var.common_tags
}

# Attach AWS Backup service role policy
resource "aws_iam_role_policy_attachment" "backup_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
  role       = aws_iam_role.backup_role.name
}

# IAM policy for RDS IAM authentication
resource "aws_iam_policy" "rds_connect_policy" {
  name        = "${var.name_prefix}rds-connect-policy"
  description = "Policy to allow IAM authentication to RDS"
  
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [ # nosemgrep: no-iam-resource-exposure
          "rds-db:connect"
        ],
        Resource = [
          "arn:aws:rds-db:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:dbuser:${aws_rds_cluster.postgres.cluster_resource_id}/*"
        ]
      }
    ]
  })
  
  tags = var.common_tags
}
