########################################################
# Parameter Store Module Outputs
########################################################

output "parameter_name" {
  description = "Name of the parameter store parameter"
  value       = aws_ssm_parameter.agentic_platform_config.name
}

output "parameter_arn" {
  description = "ARN of the parameter store parameter"
  value       = aws_ssm_parameter.agentic_platform_config.arn
}

output "parameter_version" {
  description = "Version of the parameter store parameter"
  value       = aws_ssm_parameter.agentic_platform_config.version
}

output "configuration_json" {
  description = "JSON configuration stored in parameter store"
  value       = aws_ssm_parameter.agentic_platform_config.value
  sensitive   = true
}
