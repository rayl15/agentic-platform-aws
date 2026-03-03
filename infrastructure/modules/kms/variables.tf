variable "enable_kms_encryption" {
  description = "Enable KMS encryption for resources that support it"
  type        = bool
  default     = false
}

variable "kms_deletion_window" {
  description = "Waiting period in days before KMS key is deleted"
  type        = number
  default     = 7
}

variable "kms_key_administrators" {
  description = "List of ARNs of IAM users/roles that can administer the KMS key"
  type        = list(string)
  default     = []
}

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}
