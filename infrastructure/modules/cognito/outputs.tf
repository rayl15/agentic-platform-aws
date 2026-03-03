########################################################
# Cognito Module Outputs
########################################################

# User Pool outputs
output "user_pool_id" {
  description = "ID of the Cognito User Pool"
  value       = aws_cognito_user_pool.main.id
}

output "user_pool_arn" {
  description = "ARN of the Cognito User Pool"
  value       = aws_cognito_user_pool.main.arn
}

output "user_pool_endpoint" {
  description = "Endpoint name of the Cognito User Pool"
  value       = aws_cognito_user_pool.main.endpoint
}

# User Pool Client outputs
output "web_client_id" {
  description = "ID of the web client"
  value       = aws_cognito_user_pool_client.web_client.id
}

output "m2m_client_id" {
  description = "ID of the machine-to-machine client"
  value       = aws_cognito_user_pool_client.m2m_client.id
}

# Identity Pool outputs (conditional)
output "identity_pool_id" {
  description = "ID of the Cognito Identity Pool"
  value       = var.enable_federated_identity ? aws_cognito_identity_pool.main[0].id : null
}

# Domain outputs
output "user_pool_domain" {
  description = "Domain name of the Cognito User Pool"
  value       = aws_cognito_user_pool_domain.main.domain
}

output "auth_url" {
  description = "Authentication URL for the Cognito User Pool"
  value       = "https://${aws_cognito_user_pool_domain.main.domain}.auth.${local.aws_region}.amazoncognito.com"
}

# Resource Server outputs
output "resource_server_identifier" {
  description = "Identifier of the Cognito Resource Server"
  value       = aws_cognito_resource_server.api.identifier
}

# IAM Role outputs (conditional)
output "authenticated_role_arn" {
  description = "ARN of the authenticated IAM role"
  value       = var.enable_federated_identity ? aws_iam_role.authenticated[0].arn : null
}

# Secrets Manager outputs
output "m2m_credentials_secret_arn" {
  description = "ARN of the M2M credentials secret in Secrets Manager"
  value       = aws_secretsmanager_secret.m2m_credentials.arn
}

output "m2m_credentials_secret_name" {
  description = "Name of the M2M credentials secret in Secrets Manager"
  value       = aws_secretsmanager_secret.m2m_credentials.name
}

# User Groups outputs
output "user_groups" {
  description = "Map of user group names to their details"
  value = {
    super_admin = {
      name       = aws_cognito_user_group.super_admin.name
      precedence = aws_cognito_user_group.super_admin.precedence
    }
    platform_admin = {
      name       = aws_cognito_user_group.platform_admin.name
      precedence = aws_cognito_user_group.platform_admin.precedence
    }
    platform_user = {
      name       = aws_cognito_user_group.platform_user.name
      precedence = aws_cognito_user_group.platform_user.precedence
    }
  }
}

########################################################
# Structured Configuration (for Parameter Store)
########################################################

output "config" {
  description = "Complete Cognito configuration for parameter store"
  value = {
    # Cognito User Pool
    COGNITO_USER_POOL_ID              = aws_cognito_user_pool.main.id
    COGNITO_USER_POOL_ARN             = aws_cognito_user_pool.main.arn
    COGNITO_USER_CLIENT_ID            = aws_cognito_user_pool_client.web_client.id
    COGNITO_M2M_CLIENT_ID             = aws_cognito_user_pool_client.m2m_client.id
    COGNITO_IDENTITY_POOL_ID          = var.enable_federated_identity ? aws_cognito_identity_pool.main[0].id : null
    COGNITO_DOMAIN                    = var.use_custom_domain && var.domain_name != "" ? "https://${var.environment}.${var.domain_name}" : "https://${aws_cognito_user_pool_domain.main.domain}.auth.${local.aws_region}.amazoncognito.com"
    
    # Cognito User Groups
    COGNITO_SUPER_ADMIN_GROUP_NAME    = aws_cognito_user_group.super_admin.name
    COGNITO_PLATFORM_ADMIN_GROUP_NAME = aws_cognito_user_group.platform_admin.name
    COGNITO_PLATFORM_USER_GROUP_NAME  = aws_cognito_user_group.platform_user.name
    
    # OAuth Configuration
    OAUTH_TOKEN_ENDPOINT              = "${var.use_custom_domain && var.domain_name != "" ? "https://${var.environment}.${var.domain_name}" : "https://${aws_cognito_user_pool_domain.main.domain}.auth.${local.aws_region}.amazoncognito.com"}/oauth2/token"
    
    # Secrets
    M2M_CREDENTIALS_SECRET_ARN        = aws_secretsmanager_secret.m2m_credentials.arn
  }
}
