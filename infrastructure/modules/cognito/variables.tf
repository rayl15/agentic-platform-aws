variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the application (used for Cognito callbacks). Leave as empty string to use default AWS domain."
  type        = string
  default     = ""
}

variable "use_custom_domain" {
  description = "Set to true if using a custom domain instead of AWS default domain"
  type        = bool
  default     = false
}

variable "enable_federated_identity" {
  description = "Enable Cognito Federated Identity Pool"
  type        = bool
  default     = true
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
