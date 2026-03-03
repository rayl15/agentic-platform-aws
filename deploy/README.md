# Application and Gateway Deployment

This directory contains deployment scripts for applications and gateways in the Agentic Platform. These scripts are designed to work both locally and in CI/CD pipelines for continuous deployment.

## Prerequisites

### 1. Infrastructure Deployment
Ensure the Terraform infrastructure has been deployed first. See the main [DEPLOYMENT.md](../DEPLOYMENT.md) for infrastructure setup instructions.

### 2. Cluster Essentials Bootstrap
Before deploying applications, run the cluster essentials bootstrap:

```bash
# From the project root
./bootstrap/eks-bootstrap.sh
```

This deploys:
- Storage classes
- AWS Load Balancer Controller
- External Secrets Operator
- OpenTelemetry Collectors

### 3. Database Migrations
Run database migrations before deploying applications that use the database:

```bash
./deploy/run-migrations.sh
```

This script automatically:
- Finds the bastion instance and database cluster
- Retrieves credentials from AWS Secrets Manager
- Sets up port forwarding through the bastion
- Runs Alembic migrations
- Cleans up automatically

### 4. Local Development Setup
If deploying locally, you need to set up kubectl access to the private EKS cluster using SSM port forwarding. Follow the detailed instructions in [DEPLOYMENT.md](../DEPLOYMENT.md) under "Accessing the EKS Cluster".

**Quick setup:**
```bash
# Get bastion instance ID
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=*bastion-instance*" "Name=instance-state-name,Values=running" \
  --query "Reservations[].Instances[].InstanceId" \
  --output text)

# Start port forwarding to kubectl proxy
aws ssm start-session \
  --target $INSTANCE_ID \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["8080"],"localPortNumber":["8080"]}'

# Configure kubectl (in a new terminal)
kubectl config set-cluster eks-proxy --server=http://localhost:8080
kubectl config set-credentials eks-proxy-user
kubectl config set-context eks-proxy --cluster=eks-proxy --user=eks-proxy-user
kubectl config use-context eks-proxy
```

## Available Scripts

### Database Migrations
Run database migrations:

```bash
./run-migrations.sh
```

### Individual Application Deployment
Deploy a single application or gateway:

```bash
# Deploy without building container
./deploy-application.sh <service-name>

# Deploy with container build
./deploy-application.sh <service-name> --build
```

**Examples:**
```bash
./deploy-application.sh llm-gateway --build
./deploy-application.sh memory-gateway
./deploy-application.sh retrieval-gateway --build
```

### Bulk Gateway Deployment
Deploy all gateways at once:

```bash
# Deploy all gateways without building
./deploy-gateways.sh

# Deploy all gateways with container builds
./deploy-gateways.sh --build
```

This deploys:
- `llm-gateway`
- `memory-gateway` 
- `retrieval-gateway`

### Container Building
Build and push a container to ECR:

```bash
./build-container.sh <service-name>
```

## Configuration

### Service Values Files
Each service has its own values file in `k8s/helm/values/applications/`:
- `llm-gateway-values.yaml`
- `memory-gateway-values.yaml`
- `retrieval-gateway-values.yaml`
- etc.

### AWS Configuration Overlay
The deployment scripts automatically generate an AWS configuration overlay with:
- AWS Account ID
- AWS Region
- Stack Prefix

This eliminates the need to hardcode AWS-specific values in your service configurations. The file is in the .gitignore to minimize the chance of accidentally commiting account ids. This also makes it reusable within a CI pipeline itself.

### Secret Management
Services automatically pull configuration from AWS Parameter Store via the External Secrets Operator. Each service specifies which keys it needs in its values file:

```yaml
configKeys:
  - AWS_DEFAULT_REGION
  - COGNITO_USER_POOL_ID
  - REDIS_HOST
  # etc.
```

## Service Architecture

### Gateways
- **LLM Gateway**: Handles AI model invocations and rate limiting
- **Memory Gateway**: Manages conversation memory and PostgreSQL access
- **Retrieval Gateway**: Handles knowledge base retrieval operations

### Applications
Additional application services can be deployed using the same pattern.

## Verification

Check if your services are running:

```bash
kubectl get pods
```

## CI/CD Integration
These scripts can be used for continuous deployment in CI/CD pipelines. Container builds can be parallelized for faster deployments which is what happens in teh .github/workflow actions.