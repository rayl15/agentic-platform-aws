output "config_map_name" {
  description = "Name of the created ConfigMap"
  value       = kubernetes_config_map.platform_config.metadata[0].name
}

output "config_map_namespace" {
  description = "Namespace of the created ConfigMap"
  value       = kubernetes_config_map.platform_config.metadata[0].namespace
}

output "config_map_uid" {
  description = "UID of the created ConfigMap"
  value       = kubernetes_config_map.platform_config.metadata[0].uid
}
