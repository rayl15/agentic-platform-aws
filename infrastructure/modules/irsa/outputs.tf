########################################################
# IRSA Role Outputs
########################################################

output "ebs_csi_driver_role_arn" {
  description = "ARN of the EBS CSI driver IRSA role"
  value       = aws_iam_role.ebs_csi_driver_role.arn
}

output "otel_collector_role_arn" {
  description = "ARN of the OpenTelemetry collector IRSA role"
  value       = aws_iam_role.otel_collector_role.arn
}

output "external_secrets_role_arn" {
  description = "ARN of the External Secrets Operator IRSA role"
  value       = aws_iam_role.external_secrets_role.arn
}

output "retrieval_gateway_role_arn" {
  description = "ARN of the Retrieval Gateway IRSA role"
  value       = aws_iam_role.retrieval_gateway_role.arn
}

output "memory_gateway_role_arn" {
  description = "ARN of the Memory Gateway IRSA role"
  value       = aws_iam_role.memory_gateway_role.arn
}

output "agent_role_arn" {
  description = "ARN of the Agent IRSA role"
  value       = aws_iam_role.agent_role.arn
}

output "litellm_role_arn" {
  description = "ARN of the LiteLLM IRSA role"
  value       = aws_iam_role.litellm_role.arn
}

output "load_balancer_controller_role_arn" {
  description = "ARN of the AWS Load Balancer Controller IRSA role"
  value       = aws_iam_role.load_balancer_controller_role.arn
}

########################################################
# Structured Configuration (for Parameter Store)
########################################################

output "config" {
  description = "Complete IRSA configuration for parameter store"
  value = {
    # IRSA Role ARNs
    RETRIEVAL_GATEWAY_ROLE_ARN          = aws_iam_role.retrieval_gateway_role.arn
    MEMORY_GATEWAY_ROLE_ARN             = aws_iam_role.memory_gateway_role.arn
    OTEL_COLLECTOR_ROLE_ARN             = aws_iam_role.otel_collector_role.arn
    AWS_LOAD_BALANCER_CONTROLLER_ROLE_ARN = aws_iam_role.load_balancer_controller_role.arn
    EXTERNAL_SECRETS_ROLE_ARN           = aws_iam_role.external_secrets_role.arn
    LITELLM_ROLE_ARN                    = aws_iam_role.litellm_role.arn
    AGENT_ROLE_ARN                      = aws_iam_role.agent_role.arn
    # Add the duplicate that was in the original parameterstore.tf
    LOAD_BALANCER_CONTROLLER_ROLE_ARN   = aws_iam_role.load_balancer_controller_role.arn
  }
}
