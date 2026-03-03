variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}

variable "postgres_endpoint" {
  description = "PostgreSQL cluster endpoint"
  type        = string
}

variable "postgres_port" {
  description = "PostgreSQL cluster port"
  type        = number
}

variable "postgres_cluster_resource_id" {
  description = "PostgreSQL cluster resource ID for IAM authentication"
  type        = string
}

variable "postgres_iam_username" {
  description = "PostgreSQL IAM username for LiteLLM"
  type        = string
  default     = "litellm"
}

variable "redis_endpoint" {
  description = "Redis cluster primary endpoint"
  type        = string
}

variable "redis_auth_token" {
  description = "Redis authentication token"
  type        = string
  sensitive   = true
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
