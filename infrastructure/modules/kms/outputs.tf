output "kms_key_id" {
  description = "ID of the KMS key"
  value       = var.enable_kms_encryption ? aws_kms_key.main[0].key_id : null
}

output "kms_key_arn" {
  description = "ARN of the KMS key"
  value       = var.enable_kms_encryption ? aws_kms_key.main[0].arn : null
}

output "kms_alias_name" {
  description = "Name of the KMS key alias"
  value       = var.enable_kms_encryption ? aws_kms_alias.main[0].name : null
}

output "kms_alias_arn" {
  description = "ARN of the KMS key alias"
  value       = var.enable_kms_encryption ? aws_kms_alias.main[0].arn : null
}
