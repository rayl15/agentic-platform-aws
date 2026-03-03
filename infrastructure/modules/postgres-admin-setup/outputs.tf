########################################################
# Database Outputs
########################################################

output "litellm_database_name" {
  description = "Name of the created LiteLLM database"
  value       = postgresql_database.litellm_db.name
}

########################################################
# User Credentials Outputs
########################################################

output "rds_user_credentials" {
  description = "RDS user credentials (IAM authentication - no password)"
  value = {
    username = postgresql_role.rds_user.name
    auth_method = "iam"
    password = null  # IAM authentication doesn't use passwords
  }
}

output "litellm_user_credentials" {
  description = "LiteLLM user credentials"
  value = {
    username = postgresql_role.litellm_user.name
    password = local.litellm_user_password
    auth_method = "password"
  }
  sensitive = true
}

########################################################
# Secret Outputs (referencing existing platform secret)
########################################################

output "litellm_secret_arn" {
  description = "ARN of the LiteLLM secret in AWS Secrets Manager"
  value       = data.aws_secretsmanager_secret.litellm_secret.arn
}

output "litellm_secret_name" {
  description = "Name of the LiteLLM secret in AWS Secrets Manager"
  value       = data.aws_secretsmanager_secret.litellm_secret.name
}

########################################################
# Connection Information
########################################################

output "litellm_connection_string" {
  description = "Connection string for LiteLLM database"
  value       = "postgresql://${postgresql_role.litellm_user.name}:${urlencode(local.litellm_user_password)}@${var.postgres_host}:${var.postgres_port}/${postgresql_database.litellm_db.name}"
  sensitive   = true
}

output "rds_user_connection_info" {
  description = "Connection info for RDS user (IAM authentication)"
  value = {
    username = postgresql_role.rds_user.name
    host = var.postgres_host
    port = var.postgres_port
    database = "postgres"
    auth_method = "iam"
    note = "Use IAM authentication token as password"
  }
}

########################################################
# Structured Configuration (for Parameter Store)
########################################################

output "config" {
  description = "Complete database configuration for parameter store"
  value = {
    # RDS User Configuration (IAM authentication)
    RDS_USER_USERNAME = postgresql_role.rds_user.name
    RDS_USER_AUTH_METHOD = "iam"
    RDS_USER_HOST = var.postgres_host
    RDS_USER_PORT = var.postgres_port
    RDS_USER_DATABASE = "postgres"
    
    # LiteLLM User Configuration (password authentication)
    LITELLM_USER_USERNAME = postgresql_role.litellm_user.name
    LITELLM_USER_PASSWORD = local.litellm_user_password
    LITELLM_DATABASE_NAME = postgresql_database.litellm_db.name
    LITELLM_DATABASE_URL = "postgresql://${postgresql_role.litellm_user.name}:${urlencode(local.litellm_user_password)}@${var.postgres_host}:${var.postgres_port}/${postgresql_database.litellm_db.name}"
    
    # LiteLLM Secret (existing platform secret)
    LITELLM_SECRET_ARN = data.aws_secretsmanager_secret.litellm_secret.arn
    LITELLM_SECRET_NAME = data.aws_secretsmanager_secret.litellm_secret.name
  }
  sensitive = true
}
