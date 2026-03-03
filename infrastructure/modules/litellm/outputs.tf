########################################################
# LiteLLM Module Outputs (Individual - for Terraform consumers)
########################################################

output "litellm_secret_arn" {
  description = "ARN of the LiteLLM secret in Secrets Manager"
  value       = aws_secretsmanager_secret.litellm_secret.arn
}

output "litellm_secret_name" {
  description = "Name of the LiteLLM secret in Secrets Manager"
  value       = aws_secretsmanager_secret.litellm_secret.name
}

output "litellm_master_key" {
  description = "LiteLLM master key (sensitive)"
  value       = "sk-${random_string.litellm_master_key_suffix.result}"
  sensitive   = true
}

output "agent_secret_arn" {
  description = "ARN of the agent secret in Secrets Manager"
  value       = aws_secretsmanager_secret.agent_secret.arn
}

output "postgres_iam_username" {
  description = "PostgreSQL IAM username for LiteLLM"
  value       = var.postgres_iam_username
}

output "postgres_db_user_arn" {
  description = "ARN for PostgreSQL database user IAM authentication"
  value       = "arn:aws:rds-db:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:dbuser:${var.postgres_cluster_resource_id}/${var.postgres_iam_username}"
}

########################################################
# Structured Configuration (for Parameter Store)
########################################################

output "config" {
  description = "Complete LiteLLM configuration for parameter store"
  value = {
    # LiteLLM Configuration
    LITELLM_CONFIG_SECRET_ARN = aws_secretsmanager_secret.litellm_secret.arn
    LITELLM_SECRET_NAME = aws_secretsmanager_secret.litellm_secret.name
    AGENT_LITELLM_SECRET_ARN = aws_secretsmanager_secret.agent_secret.arn
    AGENT_LITELLM_SECRET_NAME = aws_secretsmanager_secret.agent_secret.name
  }
}
