########################################################
# EKS Cluster Outputs
########################################################

output "eks_cluster_id" {
  description = "Name/ID of the EKS cluster"
  value       = module.eks.cluster_id
}

output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "eks_cluster_arn" {
  description = "ARN of the EKS cluster"
  value       = module.eks.cluster_arn
}

output "eks_cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_version" {
  description = "Kubernetes version of the EKS cluster"
  value       = module.eks.cluster_version
}

output "eks_cluster_oidc_issuer_url" {
  description = "The URL on the EKS cluster for the OpenID Connect identity provider"
  value       = module.eks.cluster_oidc_issuer_url
}

########################################################
# EKS Node Group Outputs
########################################################

output "eks_node_group_arn" {
  description = "ARN of the EKS node group"
  value       = module.eks.node_group_arn
}

output "eks_node_group_status" {
  description = "Status of the EKS node group"
  value       = module.eks.node_group_status
}

########################################################
# EKS Security Group Outputs
########################################################

output "eks_cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "eks_node_security_group_id" {
  description = "Security group ID attached to the EKS node group"
  value       = module.eks.node_security_group_id
}

########################################################
# EKS IAM Role Outputs
########################################################

output "eks_cluster_iam_role_arn" {
  description = "IAM role ARN associated with EKS cluster"
  value       = module.eks.cluster_iam_role_arn
}

output "eks_node_group_iam_role_arn" {
  description = "IAM role ARN associated with EKS node group"
  value       = module.eks.node_group_iam_role_arn
}

output "eks_deployment_role_arn" {
  description = "IAM role ARN for EKS deployment operations"
  value       = module.eks.deployment_role_arn
}

########################################################
# PostgreSQL Aurora Outputs
########################################################

output "postgres_cluster_id" {
  description = "ID of the Aurora PostgreSQL cluster"
  value       = module.postgres_aurora.cluster_id
}

output "postgres_cluster_arn" {
  description = "ARN of the Aurora PostgreSQL cluster"
  value       = module.postgres_aurora.cluster_arn
}

output "postgres_cluster_endpoint" {
  description = "Writer endpoint for the Aurora PostgreSQL cluster"
  value       = module.postgres_aurora.cluster_endpoint
}

output "postgres_cluster_reader_endpoint" {
  description = "Reader endpoint for the Aurora PostgreSQL cluster"
  value       = module.postgres_aurora.cluster_reader_endpoint
}

output "postgres_cluster_port" {
  description = "Port on which the Aurora PostgreSQL cluster accepts connections"
  value       = module.postgres_aurora.cluster_port
}

output "postgres_database_name" {
  description = "Name of the default database"
  value       = module.postgres_aurora.cluster_database_name
}

output "postgres_master_username" {
  description = "Master username for the Aurora PostgreSQL cluster"
  value       = module.postgres_aurora.cluster_master_username
  sensitive   = true
}

output "postgres_master_user_secret_arn" {
  description = "ARN of the master user secret in Secrets Manager"
  value       = module.postgres_aurora.master_user_secret_arn
}

output "postgres_security_group_id" {
  description = "ID of the PostgreSQL security group"
  value       = module.postgres_aurora.security_group_id
}

output "postgres_rds_connect_policy_arn" {
  description = "ARN of the RDS IAM authentication policy"
  value       = module.postgres_aurora.rds_connect_policy_arn
}

########################################################
# Redis Agentic Cache Outputs
########################################################

output "redis_cluster_id" {
  description = "ID of the Redis replication group"
  value       = module.redis.cluster_id
}

output "redis_cluster_arn" {
  description = "ARN of the Redis replication group"
  value       = module.redis.cluster_arn
}

output "redis_primary_endpoint" {
  description = "Primary endpoint address of the Redis cluster"
  value       = module.redis.primary_endpoint_address
}

output "redis_reader_endpoint" {
  description = "Reader endpoint address of the Redis cluster"
  value       = module.redis.reader_endpoint_address
}

output "redis_port" {
  description = "Port number on which the Redis cluster accepts connections"
  value       = module.redis.port
}

output "redis_auth_secret_arn" {
  description = "ARN of the Redis auth token secret in Secrets Manager"
  value       = module.redis.auth_secret_arn
}

output "redis_connect_policy_arn" {
  description = "ARN of the IAM policy for Redis connection and auth token access"
  value       = module.redis.connect_policy_arn
}

output "redis_security_group_id" {
  description = "ID of the Redis security group"
  value       = module.redis.security_group_id
}

########################################################
# Cognito Authentication Outputs
########################################################

output "cognito_user_pool_id" {
  description = "ID of the Cognito User Pool"
  value       = module.cognito.user_pool_id
}

output "cognito_user_pool_arn" {
  description = "ARN of the Cognito User Pool"
  value       = module.cognito.user_pool_arn
}

output "cognito_user_pool_endpoint" {
  description = "Endpoint name of the Cognito User Pool"
  value       = module.cognito.user_pool_endpoint
}

output "cognito_web_client_id" {
  description = "ID of the Cognito web client"
  value       = module.cognito.web_client_id
}

output "cognito_m2m_client_id" {
  description = "ID of the Cognito machine-to-machine client"
  value       = module.cognito.m2m_client_id
}

output "cognito_identity_pool_id" {
  description = "ID of the Cognito Identity Pool"
  value       = module.cognito.identity_pool_id
}

output "cognito_user_pool_domain" {
  description = "Domain name of the Cognito User Pool"
  value       = module.cognito.user_pool_domain
}

output "cognito_auth_url" {
  description = "Authentication URL for the Cognito User Pool"
  value       = module.cognito.auth_url
}

output "cognito_resource_server_identifier" {
  description = "Identifier of the Cognito Resource Server"
  value       = module.cognito.resource_server_identifier
}

output "cognito_authenticated_role_arn" {
  description = "ARN of the Cognito authenticated IAM role"
  value       = module.cognito.authenticated_role_arn
}

output "cognito_m2m_credentials_secret_arn" {
  description = "ARN of the M2M credentials secret in Secrets Manager"
  value       = module.cognito.m2m_credentials_secret_arn
}

output "cognito_m2m_credentials_secret_name" {
  description = "Name of the M2M credentials secret in Secrets Manager"
  value       = module.cognito.m2m_credentials_secret_name
}

output "cognito_user_groups" {
  description = "Map of Cognito user group names to their details"
  value       = module.cognito.user_groups
}

########################################################
# IRSA Role Outputs
########################################################

output "irsa_ebs_csi_driver_role_arn" {
  description = "ARN of the EBS CSI driver IRSA role"
  value       = module.irsa.ebs_csi_driver_role_arn
}

output "irsa_otel_collector_role_arn" {
  description = "ARN of the OpenTelemetry collector IRSA role"
  value       = module.irsa.otel_collector_role_arn
}

output "irsa_external_secrets_role_arn" {
  description = "ARN of the External Secrets Operator IRSA role"
  value       = module.irsa.external_secrets_role_arn
}

output "irsa_retrieval_gateway_role_arn" {
  description = "ARN of the Retrieval Gateway IRSA role"
  value       = module.irsa.retrieval_gateway_role_arn
}

output "irsa_memory_gateway_role_arn" {
  description = "ARN of the Memory Gateway IRSA role"
  value       = module.irsa.memory_gateway_role_arn
}

output "irsa_agent_role_arn" {
  description = "ARN of the Agent IRSA role"
  value       = module.irsa.agent_role_arn
}

output "irsa_litellm_role_arn" {
  description = "ARN of the LiteLLM IRSA role"
  value       = module.irsa.litellm_role_arn
}

output "irsa_load_balancer_controller_role_arn" {
  description = "ARN of the AWS Load Balancer Controller IRSA role"
  value       = module.irsa.load_balancer_controller_role_arn
}

########################################################
# LiteLLM Outputs
########################################################

output "litellm_secret_arn" {
  description = "ARN of the LiteLLM secret in Secrets Manager"
  value       = module.litellm.litellm_secret_arn
}

output "litellm_secret_name" {
  description = "Name of the LiteLLM secret in Secrets Manager"
  value       = module.litellm.litellm_secret_name
}

output "litellm_postgres_iam_username" {
  description = "PostgreSQL IAM username for LiteLLM"
  value       = module.litellm.postgres_iam_username
}

########################################################
# Bastion Outputs
########################################################

output "bastion_instance_id" {
  description = "ID of the bastion instance for SSM access"
  value       = module.bastion.bastion_instance_id
}

output "bastion_private_ip" {
  description = "Private IP address of the bastion instance"
  value       = module.bastion.bastion_private_ip
}

########################################################
# S3 Outputs
########################################################

output "s3_spa_website_bucket_name" {
  description = "Name of the S3 bucket for the SPA website"
  value       = module.s3_spa_website.bucket_name
}

output "s3_spa_website_bucket_arn" {
  description = "ARN of the S3 bucket for the SPA website"
  value       = module.s3_spa_website.bucket_arn
}

output "s3_spa_website_bucket_regional_domain_name" {
  description = "Regional domain name of the S3 bucket"
  value       = module.s3_spa_website.bucket_regional_domain_name
}

########################################################
# CloudFront Outputs
########################################################

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = module.cloudfront_spa.cloudfront_distribution_id
}

output "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = module.cloudfront_spa.cloudfront_distribution_arn
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = module.cloudfront_spa.cloudfront_domain_name
}

output "spa_website_url" {
  description = "URL of the SPA website"
  value       = module.cloudfront_spa.spa_website_url
}
