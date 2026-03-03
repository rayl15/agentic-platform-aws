########################################################
# Redis Cluster Outputs (Individual - for Terraform consumers)
########################################################

output "cluster_id" {
  description = "ID of the Redis replication group"
  value       = aws_elasticache_replication_group.redis_cache.id
}

output "cluster_arn" {
  description = "ARN of the Redis replication group"
  value       = aws_elasticache_replication_group.redis_cache.arn
}

output "primary_endpoint_address" {
  description = "Primary endpoint address of the Redis cluster"
  value       = aws_elasticache_replication_group.redis_cache.primary_endpoint_address
}

output "reader_endpoint_address" {
  description = "Reader endpoint address of the Redis cluster"
  value       = aws_elasticache_replication_group.redis_cache.reader_endpoint_address
}

output "port" {
  description = "Port number on which the Redis cluster accepts connections"
  value       = aws_elasticache_replication_group.redis_cache.port
}

output "configuration_endpoint_address" {
  description = "Configuration endpoint address of the Redis cluster"
  value       = aws_elasticache_replication_group.redis_cache.configuration_endpoint_address
}

########################################################
# Security Outputs
########################################################

output "security_group_id" {
  description = "ID of the Redis security group"
  value       = aws_security_group.redis_cache.id
}

output "security_group_arn" {
  description = "ARN of the Redis security group"
  value       = aws_security_group.redis_cache.arn
}

########################################################
# Secrets Manager Outputs
########################################################

output "auth_secret_arn" {
  description = "ARN of the Redis auth token secret in Secrets Manager"
  value       = aws_secretsmanager_secret.redis_cache_auth.arn
}

output "auth_secret_name" {
  description = "Name of the Redis auth token secret in Secrets Manager"
  value       = aws_secretsmanager_secret.redis_cache_auth.name
}

output "auth_token" {
  description = "Redis authentication token (sensitive)"
  value       = random_password.redis_cache_auth_token.result
  sensitive   = true
}

########################################################
# IAM Outputs
########################################################

output "connect_policy_arn" {
  description = "ARN of the IAM policy for Redis connection and auth token access"
  value       = aws_iam_policy.redis_cache_connect.arn
}

########################################################
# Subnet Group Outputs
########################################################

output "subnet_group_name" {
  description = "Name of the ElastiCache subnet group"
  value       = aws_elasticache_subnet_group.redis_cache.name
}

output "subnet_group_arn" {
  description = "ARN of the ElastiCache subnet group"
  value       = aws_elasticache_subnet_group.redis_cache.arn
}

########################################################
# Structured Configuration (for Parameter Store)
########################################################

output "config" {
  description = "Complete Redis configuration for parameter store"
  value = {
    # Redis Connection
    REDIS_HOST                   = aws_elasticache_replication_group.redis_cache.primary_endpoint_address
    REDIS_PORT                   = 6379
    REDIS_PASSWORD_SECRET_ARN    = aws_secretsmanager_secret.redis_cache_auth.arn
  }
}
