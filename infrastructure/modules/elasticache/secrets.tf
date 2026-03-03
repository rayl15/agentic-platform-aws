# Generate random auth token for Redis
resource "random_password" "redis_cache_auth_token" {
  length = 32
  special = false  # ElastiCache auth tokens can only contain alphanumeric characters
}

# Secrets Manager secret for Redis auth token
resource "aws_secretsmanager_secret" "redis_cache_auth" {
  # checkov:skip=CKV2_AWS_57: As a sample, its a bit heavy handed to rotate the secret. This is called out in the readme. 
  # checkov:skip=CKV_AWS_149: KMS key is conditionally used based on var.enable_kms_encryption
  name                    = "${var.name_prefix}${var.cache_name}-auth-${var.suffix}"
  description             = "Auth token for platform Redis cache cluster"
  kms_key_id              = var.enable_kms_encryption ? var.kms_key_arn : null
  recovery_window_in_days = 0  # Allow immediate deletion without waiting period
  force_overwrite_replica_secret = true  # Allow overwriting if secret exists
  
  tags = var.common_tags
}

resource "aws_secretsmanager_secret_version" "redis_cache_auth" {
  secret_id     = aws_secretsmanager_secret.redis_cache_auth.id
  secret_string = random_password.redis_cache_auth_token.result
}
