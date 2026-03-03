########################################################
# Cognito User Groups
########################################################

# Create user groups for platform access levels
resource "aws_cognito_user_group" "super_admin" {
  name         = "super_admin"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Super administrators with full system access"
  precedence   = 1  # Highest precedence
}

resource "aws_cognito_user_group" "platform_admin" {
  name         = "platform_admin"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Platform administrators with administrative access"
  precedence   = 2  # Medium precedence
}

resource "aws_cognito_user_group" "platform_user" {
  name         = "platform_user"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Regular platform users with standard access"
  precedence   = 3  # Lowest precedence
}
