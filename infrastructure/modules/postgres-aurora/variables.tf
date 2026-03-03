########################################################
# Core Variables
########################################################

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}

variable "suffix" {
  description = "Random suffix for unique resource naming"
  type        = string
}

########################################################
# Networking Variables
########################################################

variable "vpc_id" {
  description = "ID of the VPC where PostgreSQL will be deployed"
  type        = string
}

variable "vpc_cidr_block" {
  description = "CIDR block of the VPC for security group rules"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for PostgreSQL deployment"
  type        = list(string)
}

variable "eks_node_security_group_ids" {
  description = "List of EKS node security group IDs that need access to PostgreSQL"
  type        = list(string)
  default     = []
}

variable "bastion_security_group_ids" {
  description = "List of bastion security group IDs that need access to PostgreSQL"
  type        = list(string)
  default     = []
}

########################################################
# Database Configuration Variables
########################################################

variable "instance_count" {
  description = "Number of Aurora instances to create"
  type        = number
  default     = 2
}

variable "instance_class" {
  description = "Instance class for Aurora instances"
  type        = string
  default     = "db.t4g.medium"
}

variable "postgres_deletion_protection" {
  description = "Enable deletion protection for PostgreSQL cluster"
  type        = bool
  default     = true
}

########################################################
# Encryption Variables
########################################################

variable "enable_kms_encryption" {
  description = "Enable KMS encryption for PostgreSQL cluster"
  type        = bool
  default     = false
}

variable "kms_key_arn" {
  description = "ARN of the KMS key to use for encryption"
  type        = string
  default     = null
}

variable "kms_key_id" {
  description = "ID of the KMS key to use for SNS encryption"
  type        = string
  default     = null
}

########################################################
# IAM Variables
########################################################

variable "postgres_iam_username" {
  description = "PostgreSQL IAM username for applications"
  type        = string
  default     = "postgres_iam_user"
}
