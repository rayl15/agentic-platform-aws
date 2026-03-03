########################################################
# Cognito Resource Server
########################################################

# Add a resource server for API authorization
resource "aws_cognito_resource_server" "api" {
  name         = "${var.name_prefix}api-resource"
  identifier   = var.use_custom_domain ? "api.${var.environment}.${var.domain_name}" : "api.${var.environment}.${local.suffix}"
  user_pool_id = aws_cognito_user_pool.main.id
  
  scope {
    scope_name        = "read"
    scope_description = "Read access to the API"
  }
  
  scope {
    scope_name        = "write"
    scope_description = "Write access to the API"
  }
  
  scope {
    scope_name        = "admin"
    scope_description = "Admin access to the API"
  }
}
