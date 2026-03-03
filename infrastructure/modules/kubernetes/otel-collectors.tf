# OpenTelemetry Collectors
#
# This file manages the deployment of OpenTelemetry collectors for the platform.
# The collectors are deployed as infrastructure services that provide observability
# capabilities to all applications in the cluster.
#
# Components:
# - Namespace for observability resources
# - Helm release for OTEL collectors using the custom chart
# - Service account and RBAC configuration via Helm values

# Create observability namespace
resource "kubernetes_namespace" "observability" {
  metadata {
    name = "observability"
    labels = {
      name                                 = "observability"
      "pod-security.kubernetes.io/audit"   = "restricted"
      "pod-security.kubernetes.io/enforce" = "baseline"
      "pod-security.kubernetes.io/warn"    = "restricted"
    }
  }
}

# Deploy OTEL Collectors using Helm
resource "helm_release" "otel_collectors" {
  name       = "otel-collectors"
  namespace  = kubernetes_namespace.observability.metadata[0].name
  chart      = var.otel_chart_path
  
  # Values for the OTEL collectors
  values = [
    yamlencode({
      clusterName = var.cluster_name
      region      = var.aws_region
      
      serviceAccount = {
        name    = "otel-collector-sa"
        roleArn = var.otel_collector_role_arn
        create  = true
      }
      
      namespace = kubernetes_namespace.observability.metadata[0].name
    })
  ]

  # Ensure namespace exists before deploying
  depends_on = [kubernetes_namespace.observability]
  
  # Force recreation if chart values change significantly
  recreate_pods = false
  
  # Wait for deployment to be ready
  wait          = true
  wait_for_jobs = true
  timeout       = 300

  # Clean up on destroy
  cleanup_on_fail = true
}
