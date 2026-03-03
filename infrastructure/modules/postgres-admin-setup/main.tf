# PostgreSQL Administrative Setup Module
#
# This module handles the administrative setup of PostgreSQL databases, users, and secrets.
# It replaces the separate LiteLLM module and Alembic user creation migrations.
# 
# Creates:
# - rdsuser: General RDS user with IAM authentication (replaces Alembic migration)
# - litellm_user: User for LiteLLM proxy with password authentication  
# - litellm_db: Database for LiteLLM
# - Updates existing LiteLLM secret in AWS Secrets Manager with real credentials
#
# Supports both local (port forwarding) and direct connections via provider configuration.

terraform {
  required_version = ">= 1.0"
  required_providers {
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = ">= 1.21.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.1"
    }
  }
}

# Read the existing LiteLLM secret created by the platform layer
data "aws_secretsmanager_secret" "litellm_secret" {
  name = var.litellm_secret_name
}

data "aws_secretsmanager_secret_version" "litellm_secret" {
  secret_id = data.aws_secretsmanager_secret.litellm_secret.id
}

locals {
  # Parse the existing secret to get the litellm user password
  existing_secret = jsondecode(data.aws_secretsmanager_secret_version.litellm_secret.secret_string)
  litellm_user_password = local.existing_secret.POSTGRES_PASSWORD
}

########################################################
# Database Creation
########################################################

# Create LiteLLM database
resource "postgresql_database" "litellm_db" {
  name  = "litellm_db"
  owner = var.postgres_admin_username
  
  # Set encoding and locale
  encoding   = "UTF8"
  lc_collate = "en_US.UTF-8"
  lc_ctype   = "en_US.UTF-8"
}

########################################################
# User Management
########################################################

# Create RDS user with IAM authentication (no password)
resource "postgresql_role" "rds_user" {
  name     = "rdsuser"
  login    = true
  # No password - uses IAM authentication
  
  create_database = false
  create_role     = false
  inherit         = true
  replication     = false
  bypass_row_level_security = false
  connection_limit = -1
  valid_until = "infinity"
}

# Grant RDS IAM role to rds_user
resource "postgresql_grant_role" "rds_user_iam_role" {
  role             = postgresql_role.rds_user.name
  grant_role       = "rds_iam"
  with_admin_option = false
  
  depends_on = [postgresql_role.rds_user]
}

# Grant table permissions to RDS user
resource "postgresql_grant" "rds_user_tables" {
  database    = "postgres"
  role        = postgresql_role.rds_user.name
  schema      = "public"
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  
  depends_on = [postgresql_role.rds_user]
}

# Create LiteLLM user with password from existing secret
resource "postgresql_role" "litellm_user" {
  name     = "litellm"  # Use the same username as in the platform secret
  login    = true
  password = local.litellm_user_password  # Use password from existing secret
  
  create_database = false
  create_role     = false
  inherit         = true
  replication     = false
  bypass_row_level_security = false
  connection_limit = -1
  encrypted_password = true
  valid_until = "infinity"
}

# Grant permissions to LiteLLM user on LiteLLM database
resource "postgresql_grant" "litellm_user_database" {
  database    = postgresql_database.litellm_db.name
  role        = postgresql_role.litellm_user.name
  schema      = "public"
  object_type = "database"
  privileges  = ["CONNECT", "CREATE"]
  
  depends_on = [
    postgresql_role.litellm_user,
    postgresql_database.litellm_db
  ]
}

# Grant schema permissions to LiteLLM user (CRITICAL - needed for Prisma migrations)
resource "postgresql_grant" "litellm_user_schema" {
  database    = postgresql_database.litellm_db.name
  role        = postgresql_role.litellm_user.name
  schema      = "public"
  object_type = "schema"
  privileges  = ["CREATE", "USAGE"]
  
  depends_on = [
    postgresql_role.litellm_user,
    postgresql_database.litellm_db
  ]
}

# Grant table permissions to LiteLLM user
resource "postgresql_grant" "litellm_user_tables" {
  database    = postgresql_database.litellm_db.name
  role        = postgresql_role.litellm_user.name
  schema      = "public"
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  
  depends_on = [
    postgresql_role.litellm_user,
    postgresql_database.litellm_db
  ]
}

# Grant sequence permissions to LiteLLM user
resource "postgresql_grant" "litellm_user_sequences" {
  database    = postgresql_database.litellm_db.name
  role        = postgresql_role.litellm_user.name
  schema      = "public"
  object_type = "sequence"
  privileges  = ["SELECT", "UPDATE", "USAGE"]
  
  depends_on = [
    postgresql_role.litellm_user,
    postgresql_database.litellm_db
  ]
}

########################################################
# Update LiteLLM Secret with Real Database Info
########################################################

# Update the existing LiteLLM secret with real database connection info
resource "aws_secretsmanager_secret_version" "litellm_secret_update" {
  secret_id     = data.aws_secretsmanager_secret.litellm_secret.id
  secret_string = jsonencode(merge(
    local.existing_secret,
    {
      # Update with real database info now that user and database exist
      POSTGRES_USERNAME = postgresql_role.litellm_user.name
      POSTGRES_DBNAME = postgresql_database.litellm_db.name
      DATABASE_URL = "postgresql://${postgresql_role.litellm_user.name}:${urlencode(local.litellm_user_password)}@${var.postgres_host}:${var.postgres_port}/${postgresql_database.litellm_db.name}"
    }
  ))
  
  depends_on = [
    postgresql_role.litellm_user,
    postgresql_database.litellm_db
  ]
}
