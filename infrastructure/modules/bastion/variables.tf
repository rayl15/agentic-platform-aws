variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}

variable "vpc_id" {
  description = "ID of the VPC where bastion will be deployed"
  type        = string
}

variable "private_subnet_id" {
  description = "ID of the private subnet where bastion will be deployed"
  type        = string
}

variable "eks_cluster_name" {
  description = "Name of the EKS cluster for kubectl configuration"
  type        = string
}

variable "eks_cluster_arn" {
  description = "ARN of the EKS cluster for IAM permissions"
  type        = string
}

variable "rds_cluster_resource_id" {
  description = "Resource ID of the RDS cluster for IAM authentication"
  type        = string
}

variable "secrets_manager_arns" {
  description = "List of Secrets Manager ARNs that bastion needs access to"
  type        = list(string)
  default     = []
}

variable "redis_cluster_arn" {
  description = "ARN of the Redis cluster for IAM permissions"
  type        = string
}
