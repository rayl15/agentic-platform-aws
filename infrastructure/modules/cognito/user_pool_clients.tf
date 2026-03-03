########################################################
# Cognito User Pool Clients
########################################################

# App client for web applications
resource "aws_cognito_user_pool_client" "web_client" {
  name                         = "${var.name_prefix}web-client"
  user_pool_id                 = aws_cognito_user_pool.main.id
  generate_secret              = false
  refresh_token_validity       = 30
  prevent_user_existence_errors = "ENABLED"
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH"
  ]
  
  callback_urls        = var.use_custom_domain ? ["https://${var.environment}.${var.domain_name}/callback", "http://localhost:3000/callback"] : ["https://${aws_cognito_user_pool_domain.main.domain}.auth.${local.aws_region}.amazoncognito.com/oauth2/idpresponse", "http://localhost:3000/callback"]
  logout_urls          = var.use_custom_domain ? ["https://${var.environment}.${var.domain_name}/logout", "http://localhost:3000/logout"] : ["https://${aws_cognito_user_pool_domain.main.domain}.auth.${local.aws_region}.amazoncognito.com/logout", "http://localhost:3000/logout"]
  allowed_oauth_flows  = ["code", "implicit"]
  allowed_oauth_scopes = ["email", "openid", "profile"]
  supported_identity_providers = ["COGNITO"]
}

# M2M client for service-to-service communication
resource "aws_cognito_user_pool_client" "m2m_client" {
  name                           = "${var.name_prefix}m2m-client-${local.suffix}"
  user_pool_id                   = aws_cognito_user_pool.main.id
  generate_secret                = true # Required for client credentials flow
  refresh_token_validity         = 30
  access_token_validity          = 1440  # 24 hours token validity
  id_token_validity              = 1440  # 24 hours token validity 
  prevent_user_existence_errors  = "ENABLED"
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }
  
  # Client credentials is the key flow for M2M
  allowed_oauth_flows  = ["client_credentials"]
  
  # IMPORTANT: Add this parameter
  allowed_oauth_flows_user_pool_client = true
  
  # Use the existing resource server's scopes
  allowed_oauth_scopes = [
    "${aws_cognito_resource_server.api.identifier}/read",
    "${aws_cognito_resource_server.api.identifier}/write",
  ]
  supported_identity_providers = ["COGNITO"]
}
