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

variable "cluster_oidc_issuer_url" {
  description = "OIDC issuer URL from the EKS cluster"
  type        = string
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

########################################################
# OpenSearch Variables
########################################################

variable "opensearch_domain_arn" {
  description = "ARN of the OpenSearch domain for OTEL collector access"
  type        = string
  default     = null
}

########################################################
# Secrets Manager Variables
########################################################

variable "secrets_manager_arns" {
  description = "List of Secrets Manager ARNs for External Secrets Operator access"
  type        = list(string)
  default     = []
}

variable "parameter_store_arns" {
  description = "List of Parameter Store ARNs for External Secrets Operator access"
  type        = list(string)
  default     = []
}

########################################################
# Redis Variables
########################################################

variable "redis_cluster_arns" {
  description = "List of Redis cluster ARNs for LLM Gateway access"
  type        = list(string)
  default     = []
}

variable "redis_secret_arns" {
  description = "List of Redis secret ARNs for LLM Gateway access"
  type        = list(string)
  default     = []
}

########################################################
# PostgreSQL Variables
########################################################

variable "postgres_secret_arns" {
  description = "List of PostgreSQL secret ARNs for Memory Gateway access"
  type        = list(string)
  default     = []
}

variable "postgres_db_user_arns" {
  description = "List of PostgreSQL database user ARNs for Memory Gateway IAM auth"
  type        = list(string)
  default     = []
}

########################################################
# LiteLLM Variables
########################################################

variable "litellm_secret_arns" {
  description = "List of LiteLLM secret ARNs for LiteLLM access"
  type        = list(string)
  default     = []
}

variable "litellm_postgres_db_user_arns" {
  description = "List of PostgreSQL database user ARNs for LiteLLM IAM auth"
  type        = list(string)
  default     = []
}

########################################################
# Agent Variables
########################################################

variable "agent_secret_arns" {
  description = "List of agent secret ARNs for agent access"
  type        = list(string)
  default     = []
}
