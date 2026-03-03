# Generate a random password for PostgreSQL IAM user
resource "random_password" "postgres_iam_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Generate a secure master key for LiteLLM that starts with "sk-"
resource "random_string" "litellm_master_key_suffix" {
  length  = 48
  special = false
}

# Create a consolidated secret for LiteLLM with all credentials and configuration
resource "aws_secretsmanager_secret" "litellm_secret" {
  # checkov:skip=CKV2_AWS_57: As a sample, its a bit heavy handed to rotate the secret. This is called out in the readme. 
  # checkov:skip=CKV_AWS_149: KMS key is conditionally used based on var.enable_kms_encryption
  name                    = "${var.name_prefix}litellm-secret"
  description             = "Consolidated secret for LiteLLM proxy"
  recovery_window_in_days = 0  # Allow immediate deletion without waiting period
  kms_key_id              = var.enable_kms_encryption ? var.kms_key_arn : null
  
  tags = var.common_tags
}

resource "aws_secretsmanager_secret_version" "litellm_secret" {
  secret_id     = aws_secretsmanager_secret.litellm_secret.id
  secret_string = jsonencode({
    # LiteLLM master key
    LITELLM_MASTER_KEY = "sk-${random_string.litellm_master_key_suffix.result}"
    
    # PostgreSQL credentials
    POSTGRES_USERNAME = var.postgres_iam_username
    POSTGRES_PASSWORD = random_password.postgres_iam_password.result
    POSTGRES_HOST = var.postgres_endpoint
    POSTGRES_PORT = var.postgres_port
    POSTGRES_DBNAME = "litellm_db"
    DATABASE_URL = "postgresql://${var.postgres_iam_username}:${urlencode(random_password.postgres_iam_password.result)}@${var.postgres_endpoint}:${var.postgres_port}/litellm_db"
    
    # Redis credentials - now included in this secret
    REDIS_HOST = var.redis_endpoint
    REDIS_PORT = 6379
    REDIS_USERNAME = ""  # Redis doesn't use username with auth token
    REDIS_PASSWORD = var.redis_auth_token
  })
}
