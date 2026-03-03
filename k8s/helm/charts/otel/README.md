# ADOT Collector Helm Chart

A simple Helm chart for deploying collectors managed by an Otel Operator (AWS Distro for OpenTelemetry (ADOT)) to send metrics, logs, and traces to AWS services.

## Configuration

Update `values.yaml` with your specific configuration:

```yaml
clusterName: "your-eks-cluster"
region: "us-west-2"
irsaRoleArn: "arn:aws:iam::123456789012:role/otel-collector-role"
namespace: "observability"
```

## Installation

The recommended way to deploy is using the script provided in `deploy/deploy-otel-collectors.sh`, which automatically pulls the IRSA role from Terraform outputs:

```bash
# Run the deployment script
. ./deploy/deploy-otel-collectors.sh
```

## OTLP Protocol and Vendor Agnostic Approach

This setup uses the OpenTelemetry Protocol (OTLP) for all telemetry data, which provides several key benefits:

1. **Application Instrumentation Stability**: Applications only need to implement OTLP once and don't need to change when backend systems change
2. **Vendor Neutrality**: The collector can send data to any supported backend by simply changing exporters
3. **Future-Proof**: As new observability systems emerge, only the collector configuration needs updating

While this chart is currently configured to export to AWS services (CloudWatch, X-Ray), the exporters can be easily modified to send data to any vendor supporting OTLP.

This separation between data collection and export destinations allows for a clean architecture and maximum flexibility.

## Usage

Applications should send telemetry data to:

- **Metrics**: `metrics-collector.observability.svc.cluster.local:4317` (gRPC) or `:4318` (HTTP)
- **Logs**: `logs-collector.observability.svc.cluster.local:4317` (gRPC) or `:4318` (HTTP)
- **Traces**: `trace-collector.observability.svc.cluster.local:4317` (gRPC) or `:4318` (HTTP)

## Testing

You can test metrics collection using the following command:

```bash
kubectl run otel-metric-test --image=ghcr.io/open-telemetry/opentelemetry-collector-contrib/telemetrygen:latest -- \
  --otlp-insecure \
  --otlp-endpoint=metrics-collector.observability.svc.cluster.local:4317 \
  --rate=10 \
  metrics
```

This test pod will send metrics to the collector and exit. It's normal for the pod to show "CrashLoopBackOff" after it completes its task.

## Viewing Telemetry Data

- **Metrics**: CloudWatch Metrics under namespace "EKS/ContainerInsights"
- **Logs**: CloudWatch Logs under "/aws/containerinsights/[CLUSTER_NAME]/application"
- **Traces**: AWS X-Ray traces console

## Architecture

This chart deploys three separate collectors:

1. **metrics**: Collects and exports metrics to CloudWatch (deployed as a DaemonSet)
2. **logs**: Collects container logs and exports to CloudWatch Logs (deployed as a DaemonSet)
3. **trace**: Collects traces and exports to AWS X-Ray (deployed as a Deployment)

The metrics and logs collectors run as DaemonSets to ensure coverage across all nodes in the cluster, while the trace collector runs as a Deployment for centralized trace collection and optimal scalability.

## Extending to Other Backends

To switch or add exporters for other backends, modify the appropriate collector YAML and add the required exporter configuration. For example, to add Prometheus:

```yaml
exporters:
  awsemf: # Existing AWS exporter
    region: {{ .Values.region }}
    namespace: EKS/ContainerInsights
    log_group_name: /aws/containerinsights/{{ .Values.clusterName }}/performance
  prometheus:
    endpoint: "0.0.0.0:8889"

service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch, resourcedetection]
      exporters: [awsemf, prometheus]  # Send to both destinations
```