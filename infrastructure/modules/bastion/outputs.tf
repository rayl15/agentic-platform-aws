output "bastion_instance_id" {
  description = "ID of the bastion instance for SSM access"
  value       = aws_instance.bastion.id
}

output "bastion_instance_arn" {
  description = "ARN of the bastion instance"
  value       = aws_instance.bastion.arn
}

output "bastion_private_ip" {
  description = "Private IP address of the bastion instance"
  value       = aws_instance.bastion.private_ip
}

output "bastion_security_group_id" {
  description = "ID of the bastion security group"
  value       = aws_security_group.bastion_sg.id
}

output "bastion_iam_role_arn" {
  description = "ARN of the bastion IAM role"
  value       = aws_iam_role.bastion_role.arn
}

output "bastion_iam_role_name" {
  description = "Name of the bastion IAM role"
  value       = aws_iam_role.bastion_role.name
}

########################################################
# Structured Configuration (for Parameter Store)
########################################################

output "config" {
  description = "Complete bastion configuration for parameter store"
  value = {
    # Bastion Instance
    BASTION_INSTANCE_ID = aws_instance.bastion.id
    BASTION_PRIVATE_IP  = aws_instance.bastion.private_ip
  }
}
