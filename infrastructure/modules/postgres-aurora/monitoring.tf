# SNS Topic for RDS Event Notifications with KMS encryption
resource "aws_sns_topic" "postgres_events" {
  name = "${var.name_prefix}postgres-events"
  kms_master_key_id = var.enable_kms_encryption ? var.kms_key_id : "alias/aws/sns"  # Use AWS managed key if custom KMS not enabled
  
  tags = var.common_tags
}

# RDS Event Subscription - fix invalid event category
resource "aws_db_event_subscription" "postgres_events" {
  name      = "${var.name_prefix}postgres-event-subscription"
  sns_topic = aws_sns_topic.postgres_events.arn
  
  source_type = "db-cluster"
  source_ids  = [aws_rds_cluster.postgres.id]
  
  # Event categories to monitor - removing "restoration" which isn't valid for db-cluster
  event_categories = [
    "failover",
    "failure",
    "maintenance",
    "notification",
    "creation",
    "deletion",
    "configuration change"
  ]
  
  enabled = true
  tags    = var.common_tags
}
