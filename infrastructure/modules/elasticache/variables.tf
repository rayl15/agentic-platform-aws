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
# Cache Naming Variables
########################################################

variable "cache_name" {
  description = "Name identifier for the cache (used in resource names)"
  type        = string
  default     = "cache"
}

variable "cache_purpose" {
  description = "Description of cache purpose (used in descriptions)"
  type        = string
  default     = "general caching"
}

########################################################
# Networking Variables
########################################################

variable "vpc_id" {
  description = "ID of the VPC where Redis will be deployed"
  type        = string
}

variable "vpc_cidr_block" {
  description = "CIDR block of the VPC for security group rules"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for Redis deployment"
  type        = list(string)
}

########################################################
# Redis Configuration Variables
########################################################

variable "node_type" {
  description = "Instance class for Redis nodes"
  type        = string
  default     = "cache.t4g.micro"
}

variable "engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.0"
}

variable "num_cache_clusters" {
  description = "Number of cache clusters (nodes) in the replication group"
  type        = number
  default     = 2
}

variable "maintenance_window" {
  description = "Maintenance window for Redis cluster"
  type        = string
  default     = "mon:03:00-mon:04:00"
}

variable "snapshot_window" {
  description = "Daily time range for automated backups"
  type        = string
  default     = "02:00-03:00"
}

variable "snapshot_retention_limit" {
  description = "Number of days to retain automatic snapshots"
  type        = number
  default     = 1
}

########################################################
# Encryption Variables
########################################################

variable "enable_kms_encryption" {
  description = "Enable KMS encryption for Redis cluster"
  type        = bool
  default     = false
}

variable "kms_key_arn" {
  description = "ARN of the KMS key to use for encryption"
  type        = string
  default     = null
}
