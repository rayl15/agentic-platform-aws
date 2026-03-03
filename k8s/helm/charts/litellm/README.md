# LiteLLM Helm Chart

This Helm chart deploys LiteLLM proxy to a Kubernetes cluster.

## Prerequisites

- Kubernetes 1.16+
- Helm 3.0+
- AWS CLI configured with appropriate permissions
- External Secrets Operator installed in the cluster
- AWS Load Balancer Controller installed in the cluster

## Installation

### 1. Apply Terraform Configuration

First, apply the Terraform configuration to create the necessary AWS resources:

```bash
cd infrastructure/terraform
terraform init
terraform apply
```

This will create:
- A master key for LiteLLM stored in AWS Secrets Manager
- A database URL secret for LiteLLM stored in AWS Secrets Manager
- IAM roles and policies for LiteLLM to access AWS services
- Parameter Store entries for LiteLLM configuration

### 2. Run Database Migrations

Run the database migrations for LiteLLM:

```bash
./deploy/run-litellm-migrations.sh
```

### 3. Deploy LiteLLM to Kubernetes

Deploy LiteLLM to Kubernetes:

```bash
./deploy/deploy-litellm.sh
```

### 4. Debug the Deployment

If you encounter any issues, you can debug the deployment:

```bash
./deploy/debug-litellm.sh
```

### 5. Update the Configuration

If you need to update the configuration:

```bash
./deploy/update-litellm-config.sh
```

## Configuration

The following table lists the configurable parameters of the LiteLLM chart and their default values.

| Parameter | Description | Default |
| --------- | ----------- | ------- |
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `ghcr.io/berriai/litellm` |
| `image.tag` | Image tag | `main-latest` |
| `image.pullPolicy` | Image pull policy | `Always` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `4000` |
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class name | `alb` |
| `ingress.annotations` | Ingress annotations | See values.yaml |
| `ingress.hosts` | Ingress hosts | See values.yaml |
| `serviceAccount.name` | Service account name | `litellm-sa` |
| `serviceAccount.create` | Create service account | `true` |
| `serviceAccount.irsaRoleName` | IRSA role name | `litellm-role` |
| `database.host` | Database host | `""` |
| `database.port` | Database port | `5432` |
| `database.name` | Database name | `postgres` |
| `database.user` | Database user | `postgres` |
| `redis.host` | Redis host | `""` |
| `redis.port` | Redis port | `6379` |
| `litellm.ui` | Enable UI | `true` |
| `litellm.masterKey` | Master key | `""` |

## Architecture

The LiteLLM deployment consists of the following components:

1. **LiteLLM Proxy**: The main application that handles API requests and routes them to the appropriate LLM provider.
2. **PostgreSQL Database**: Used to store API keys, usage logs, and other data.
3. **Redis**: Used for rate limiting and caching.
4. **AWS Secrets Manager**: Used to store sensitive information like the master key and database URL.
5. **AWS Parameter Store**: Used to store configuration values.
6. **External Secrets Operator**: Used to sync secrets from AWS Secrets Manager to Kubernetes.
7. **AWS Load Balancer Controller**: Used to create an ALB for the ingress.

## Troubleshooting

If you encounter any issues, check the following:

1. **Pod Status**: Check if the pods are running correctly.
2. **Pod Logs**: Check the logs for any errors.
3. **Secrets**: Check if the secrets are created correctly.
4. **ConfigMaps**: Check if the ConfigMaps are created correctly.
5. **External Secrets**: Check if the External Secrets are created correctly.
6. **Connectivity**: Check if the pod can connect to Redis and PostgreSQL.
7. **Environment Variables**: Check if the environment variables are set correctly.

You can use the debug script to check all of these:

```bash
./deploy/debug-litellm.sh
```
