# AWS Backup Vault for PostgreSQL cluster with correct KMS key reference
resource "aws_backup_vault" "postgres" {
  # checkov:skip=CKV_AWS_166: "Optional KMS key."
  name = "${var.name_prefix}pg-vault"
  
  # Use KMS key only if enable_kms_encryption is true, otherwise use null
  # AWS will use its own encryption if we don't specify a key
  kms_key_arn = var.enable_kms_encryption ? var.kms_key_arn : null

  force_destroy = true
  
  tags = var.common_tags
}

# AWS Backup Plan for PostgreSQL cluster - simplified name
resource "aws_backup_plan" "postgres" {
  name = "${var.name_prefix}pg-backup-plan"

  rule {
    rule_name         = "daily-backup"
    target_vault_name = aws_backup_vault.postgres.name
    schedule          = "cron(0 2 * * ? *)"  # Daily at 2:00 AM UTC
    
    lifecycle {
      delete_after = 35  # Keep backups for 35 days
    }
  }

  tags = var.common_tags
}

resource "aws_backup_selection" "postgres" {
  name         = "${var.name_prefix}pg-backup"
  iam_role_arn = aws_iam_role.backup_role.arn
  plan_id      = aws_backup_plan.postgres.id

  resources = [
    aws_rds_cluster.postgres.arn
  ]
}
