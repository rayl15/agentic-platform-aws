# Parameter group for cluster level with supported extensions
resource "aws_rds_cluster_parameter_group" "postgres" {
  name   = "${var.name_prefix}postgres-params"
  family = "aurora-postgresql16"

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"  # Using a supported extension
  }

  parameter {
    name  = "log_statement"
    value = "ddl"
  }
  
  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  tags = var.common_tags
}

# Instance parameter group
resource "aws_db_parameter_group" "postgres" {
  name   = "${var.name_prefix}postgres-instance-params"
  family = "aurora-postgresql16"

  tags = var.common_tags
}
