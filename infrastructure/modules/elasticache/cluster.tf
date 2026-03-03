# ElastiCache Redis replication group
resource "aws_elasticache_replication_group" "redis_cache" {
  # checkov:skip=CKV_AWS_31: Using auth token authentication
  # checkov:skip=CKV_AWS_191: KMS key is conditionally used based on var.enable_kms_encryption
  replication_group_id       = "${var.name_prefix}${var.cache_name}"
  description               = "Redis cluster for ${var.cache_purpose}"
  node_type                 = var.node_type
  port                      = 6379
  engine_version           = var.engine_version
  parameter_group_name     = aws_elasticache_parameter_group.redis_cache.name
  automatic_failover_enabled = true
  multi_az_enabled         = true
  num_cache_clusters       = var.num_cache_clusters

  subnet_group_name    = aws_elasticache_subnet_group.redis_cache.name
  security_group_ids   = [aws_security_group.redis_cache.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  kms_key_id               = var.enable_kms_encryption ? var.kms_key_arn : null

  auth_token = random_password.redis_cache_auth_token.result

  auto_minor_version_upgrade = true
  maintenance_window        = var.maintenance_window
  snapshot_window          = var.snapshot_window
  snapshot_retention_limit = var.snapshot_retention_limit

  tags = var.common_tags
}
