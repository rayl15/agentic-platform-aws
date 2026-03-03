########################################################
# Cluster Outputs (Individual - for Terraform consumers)
########################################################

output "cluster_id" {
  description = "ID of the Aurora PostgreSQL cluster"
  value       = aws_rds_cluster.postgres.id
}

output "cluster_arn" {
  description = "ARN of the Aurora PostgreSQL cluster"
  value       = aws_rds_cluster.postgres.arn
}

output "cluster_endpoint" {
  description = "Writer endpoint for the Aurora PostgreSQL cluster"
  value       = aws_rds_cluster.postgres.endpoint
}

output "cluster_reader_endpoint" {
  description = "Reader endpoint for the Aurora PostgreSQL cluster"
  value       = aws_rds_cluster.postgres.reader_endpoint
}

output "cluster_port" {
  description = "Port on which the Aurora PostgreSQL cluster accepts connections"
  value       = aws_rds_cluster.postgres.port
}

output "cluster_database_name" {
  description = "Name of the default database"
  value       = aws_rds_cluster.postgres.database_name
}

output "cluster_master_username" {
  description = "Master username for the Aurora PostgreSQL cluster"
  value       = aws_rds_cluster.postgres.master_username
  sensitive   = true
}

output "cluster_resource_id" {
  description = "Resource ID of the Aurora PostgreSQL cluster"
  value       = aws_rds_cluster.postgres.cluster_resource_id
}

########################################################
# Instance Outputs
########################################################

output "instance_ids" {
  description = "List of Aurora instance IDs"
  value       = aws_rds_cluster_instance.postgres[*].id
}

output "instance_endpoints" {
  description = "List of Aurora instance endpoints"
  value       = aws_rds_cluster_instance.postgres[*].endpoint
}

########################################################
# Security Outputs
########################################################

output "security_group_id" {
  description = "ID of the PostgreSQL security group"
  value       = aws_security_group.postgres.id
}

output "security_group_arn" {
  description = "ARN of the PostgreSQL security group"
  value       = aws_security_group.postgres.arn
}

########################################################
# Secrets Manager Outputs
########################################################

output "master_user_secret_arn" {
  description = "ARN of the master user secret in Secrets Manager"
  value       = aws_rds_cluster.postgres.master_user_secret[0].secret_arn
}

output "master_user_secret_kms_key_id" {
  description = "KMS key ID used to encrypt the master user secret"
  value       = aws_rds_cluster.postgres.master_user_secret[0].kms_key_id
}

########################################################
# Backup Outputs
########################################################

output "backup_vault_name" {
  description = "Name of the AWS Backup vault"
  value       = aws_backup_vault.postgres.name
}

output "backup_vault_arn" {
  description = "ARN of the AWS Backup vault"
  value       = aws_backup_vault.postgres.arn
}

output "backup_plan_id" {
  description = "ID of the AWS Backup plan"
  value       = aws_backup_plan.postgres.id
}

output "backup_plan_arn" {
  description = "ARN of the AWS Backup plan"
  value       = aws_backup_plan.postgres.arn
}

########################################################
# Monitoring Outputs
########################################################

output "sns_topic_arn" {
  description = "ARN of the SNS topic for RDS events"
  value       = aws_sns_topic.postgres_events.arn
}

output "event_subscription_arn" {
  description = "ARN of the RDS event subscription"
  value       = aws_db_event_subscription.postgres_events.arn
}

########################################################
# IAM Outputs
########################################################

output "rds_connect_policy_arn" {
  description = "ARN of the RDS IAM authentication policy"
  value       = aws_iam_policy.rds_connect_policy.arn
}

output "monitoring_role_arn" {
  description = "ARN of the RDS monitoring IAM role"
  value       = aws_iam_role.rds_monitoring.arn
}

output "backup_role_arn" {
  description = "ARN of the AWS Backup IAM role"
  value       = aws_iam_role.backup_role.arn
}

########################################################
# Structured Configuration (for Parameter Store)
########################################################

output "config" {
  description = "Complete PostgreSQL configuration for parameter store"
  value = {
    # Database Connection
    PG_WRITER_ENDPOINT            = aws_rds_cluster.postgres.endpoint
    PG_READER_ENDPOINT            = aws_rds_cluster.postgres.reader_endpoint
    POSTGRES_CLUSTER_ID           = aws_rds_cluster.postgres.id
    PG_PORT                       = aws_rds_cluster.postgres.port
    PG_DATABASE                   = aws_rds_cluster.postgres.database_name
    POSTGRES_MASTER_USERNAME      = aws_rds_cluster.postgres.master_username
    
    # IAM Users (these would be created by applications)
    PG_USER                       = var.postgres_iam_username
    PG_READ_ONLY_USER             = var.postgres_iam_username
    
    # Secrets
    PG_PASSWORD_SECRET_ARN        = aws_rds_cluster.postgres.master_user_secret[0].secret_arn
    
    # Infrastructure
    POSTGRES_SECURITY_GROUP_ID    = aws_security_group.postgres.id
    POSTGRES_PARAMETER_GROUP_NAME = aws_rds_cluster_parameter_group.postgres.name
    POSTGRES_BACKUP_VAULT_NAME    = aws_backup_vault.postgres.name
    POSTGRES_SNS_TOPIC_ARN        = aws_sns_topic.postgres_events.arn
  }
}
