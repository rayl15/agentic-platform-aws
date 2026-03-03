########################################################
# Connection Variables
########################################################

variable "postgres_host" {
  description = "PostgreSQL host endpoint"
  type        = string
}

variable "postgres_port" {
  description = "PostgreSQL port"
  type        = number
  default     = 5432
}

variable "postgres_admin_username" {
  description = "PostgreSQL admin username"
  type        = string
}

variable "postgres_admin_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}

########################################################
# AWS Secret Management Variables
########################################################

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}

variable "enable_kms_encryption" {
  description = "Enable KMS encryption for secrets"
  type        = bool
  default     = false
}

variable "kms_key_arn" {
  description = "ARN of the KMS key to use for encryption"
  type        = string
  default     = null
}
variable "litellm_secret_name" {
  description = "Name of the existing LiteLLM secret in AWS Secrets Manager"
  type        = string
}
