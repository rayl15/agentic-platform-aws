########################################################
# Platform Configuration ConfigMap
########################################################

resource "kubernetes_config_map" "platform_config" {
  # checkov:skip=CKV_K8S_21: "For a sample repo, the agents all run in the same namespace for easy discoverability"
  metadata {
    name      = var.config_map_name
    namespace = var.namespace

    labels = {
      "app.kubernetes.io/name"       = "platform-config"
      "app.kubernetes.io/component"  = "configuration"
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  # Configuration data passed from the calling module
  data = var.configuration_data
}
