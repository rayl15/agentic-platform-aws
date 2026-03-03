# ElastiCache parameter group for Redis optimization
resource "aws_elasticache_parameter_group" "redis_cache" {
  family = "redis7"
  name   = "${var.name_prefix}${var.cache_name}"
  
  tags = var.common_tags
}
