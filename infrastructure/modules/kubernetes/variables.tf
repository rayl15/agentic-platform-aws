########################################################
# ConfigMap Variables
########################################################

variable "config_map_name" {
  description = "Name of the ConfigMap to create"
  type        = string
  default     = "agentic-platform-config"
}

variable "namespace" {
  description = "Kubernetes namespace for the ConfigMap"
  type        = string
  default     = "default"
}

variable "configuration_data" {
  description = "Configuration data for the ConfigMap"
  type        = map(string)
}

########################################################
# Storage Class Variables
########################################################

variable "storage_class_name" {
  description = "Name of the storage class to create"
  type        = string
  default     = "gp3"
}

########################################################
# External Secrets Operator Variables
########################################################

variable "external_secrets_service_account_role_arn" {
  description = "IAM role ARN for External Secrets Operator service account"
  type        = string
  default     = ""
}

########################################################
# AWS Load Balancer Controller Variables
########################################################

variable "aws_load_balancer_controller_service_account_role_arn" {
  description = "IAM role ARN for AWS Load Balancer Controller service account"
  type        = string
  default     = ""
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the EKS cluster is deployed"
  type        = string
}

########################################################
# OTEL Collectors Variables
########################################################

variable "otel_chart_path" {
  description = "Path to the OTEL collectors Helm chart"
  type        = string
}

variable "otel_collector_role_arn" {
  description = "IAM role ARN for OTEL collector service account"
  type        = string
}
