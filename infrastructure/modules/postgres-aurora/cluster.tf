# Aurora PostgreSQL Cluster with Checkov suppressions
resource "aws_rds_cluster" "postgres" {
  # checkov:skip=CKV_AWS_327: "Encryption is configurable via the enable_kms_encryption variable"
  cluster_identifier      = "${var.name_prefix}postgres"
  engine                  = "aurora-postgresql"
  engine_version          = "16.6"
  database_name           = "postgres"
  master_username         = "postgres"
  # Use Secrets Manager to manage the password instead of hardcoding it
  manage_master_user_password = true
  iam_database_authentication_enabled = true
  storage_encrypted       = true
  # KMS encryption is conditionally enabled based on var.enable_kms_encryption
  kms_key_id              = var.enable_kms_encryption ? var.kms_key_arn : null
  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  preferred_maintenance_window = "sat:05:00-sat:06:00"
  skip_final_snapshot     = false
  final_snapshot_identifier = "${var.name_prefix}postgres-final-snapshot-${var.suffix}"
  
  vpc_security_group_ids = [aws_security_group.postgres.id]
  db_subnet_group_name   = aws_db_subnet_group.postgres.name

  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  deletion_protection = var.postgres_deletion_protection
  copy_tags_to_snapshot = true
  
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.postgres.name
  
  tags = merge(
    var.common_tags,
    {
      Name = "Postgres"
    }
  )
}

resource "aws_rds_cluster_instance" "postgres" {
  # checkov:skip=CKV_AWS_354: "Performance Insights encryption is configurable via the enable_kms_encryption variable"
  count                = var.instance_count
  identifier           = "${var.name_prefix}postgres-${count.index}"
  cluster_identifier   = aws_rds_cluster.postgres.id
  instance_class       = var.instance_class
  engine               = aws_rds_cluster.postgres.engine
  engine_version       = aws_rds_cluster.postgres.engine_version

  auto_minor_version_upgrade = true
  performance_insights_enabled = true
  performance_insights_kms_key_id = var.enable_kms_encryption ? var.kms_key_arn : null
  monitoring_interval        = 60
  monitoring_role_arn       = aws_iam_role.rds_monitoring.arn
  db_parameter_group_name    = aws_db_parameter_group.postgres.name
  
  tags = var.common_tags
}
