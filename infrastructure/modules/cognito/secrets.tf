########################################################
# Secrets Manager for M2M Credentials
########################################################

# Store M2M credentials in Secrets Manager for secure access
resource "aws_secretsmanager_secret" "m2m_credentials" {
  # checkov:skip=CKV2_AWS_57: As a sample, its a bit heavy handed to rotate the secret. This is called out in the readme. 
  # checkov:skip=CKV_AWS_149: KMS key is conditionally used based on var.enable_kms_encryption
  name                    = "${var.name_prefix}m2mcreds-${local.suffix}"
  description             = "Machine-to-machine client credentials for service auth"
  kms_key_id              = var.enable_kms_encryption ? var.kms_key_arn : null
  recovery_window_in_days = 0  # Allow immediate deletion without waiting period
  force_overwrite_replica_secret = true  # Allow overwriting if secret exists
  
  tags = var.common_tags
}

resource "aws_secretsmanager_secret_version" "m2m_credentials" {
  secret_id     = aws_secretsmanager_secret.m2m_credentials.id
  secret_string = jsonencode({
    client_id     = aws_cognito_user_pool_client.m2m_client.id
    client_secret = aws_cognito_user_pool_client.m2m_client.client_secret
    token_url     = "${var.use_custom_domain && var.domain_name != "" ? "https://${var.environment}.${var.domain_name}" : "https://${aws_cognito_user_pool_domain.main.domain}.auth.${local.aws_region}.amazoncognito.com"}/oauth2/token"
    scopes        = join(" ", [
      "${aws_cognito_resource_server.api.identifier}/read",
      "${aws_cognito_resource_server.api.identifier}/write",
    ])
  })
}
