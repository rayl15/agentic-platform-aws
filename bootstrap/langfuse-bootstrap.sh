#!/bin/bash

NAMESPACE="langfuse"
RELEASE_NAME="langfuse"
CHART_REPO="langfuse"
CHART_NAME="langfuse/langfuse"
VALUES_FILE="k8s/helm/values/optional/langfuse-values.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to generate secure random passwords
generate_password() {
    local length=${1:-32}
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# Function to generate hex key
generate_hex_key() {
    openssl rand -hex 32
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    local missing_commands=()
    
    if ! command_exists kubectl; then
        missing_commands+=("kubectl")
    fi
    
    if ! command_exists helm; then
        missing_commands+=("helm")
    fi
    
    if ! command_exists openssl; then
        missing_commands+=("openssl")
    fi
    
    if [ ${#missing_commands[@]} -ne 0 ]; then
        log_error "Missing required commands: ${missing_commands[*]}"
        log_error "Please install the missing commands and try again."
        exit 1
    fi
    
    # Check kubectl connectivity
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "Cannot connect to Kubernetes cluster. Please check your kubectl configuration."
        exit 1
    fi
    
    log_success "All prerequisites check passed!"
}

# Function to create namespace
create_namespace() {
    log_info "Creating namespace '$NAMESPACE'..."
    if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
        log_warning "Namespace '$NAMESPACE' already exists."
    else
        kubectl create namespace "$NAMESPACE"
        log_success "Namespace '$NAMESPACE' created."
    fi
}

# Function to generate and create secrets
create_secrets() {
    log_info "Generating secure credentials..."
    
    # Generate all passwords and keys
    local langfuse_salt=$(generate_password 16)
    local nextauth_secret=$(generate_hex_key)
    local encryption_key=$(generate_hex_key)
    local postgres_password=$(generate_password 24)
    local clickhouse_password=$(generate_password 24)
    local redis_password=$(generate_password 24)
    local s3_root_user="admin"
    local s3_root_password=$(generate_password 24)
    
    log_info "Creating Kubernetes secrets..."
    
    # Delete existing secrets if they exist (to ensure clean state)
    kubectl delete secret langfuse-general langfuse-postgresql-auth langfuse-clickhouse-auth langfuse-redis-auth langfuse-s3-auth -n "$NAMESPACE" --ignore-not-found=true
    
    # Create secrets
    kubectl create secret generic langfuse-general \
        --from-literal=salt="$langfuse_salt" \
        --from-literal=nextauth-secret="$nextauth_secret" \
        --from-literal=encryption-key="$encryption_key" \
        --namespace="$NAMESPACE"
    
    kubectl create secret generic langfuse-postgresql-auth \
        --from-literal=password="$postgres_password" \
        --namespace="$NAMESPACE"
    
    kubectl create secret generic langfuse-clickhouse-auth \
        --from-literal=password="$clickhouse_password" \
        --namespace="$NAMESPACE"
    
    kubectl create secret generic langfuse-redis-auth \
        --from-literal=password="$redis_password" \
        --namespace="$NAMESPACE"
    
    kubectl create secret generic langfuse-s3-auth \
        --from-literal=rootUser="$s3_root_user" \
        --from-literal=rootPassword="$s3_root_password" \
        --namespace="$NAMESPACE"
    
    log_success "All secrets created successfully!"
    
    # Package secrets into a single JSON object
    local secrets_json=$(cat << EOF
{
  "langfuse_salt": "$langfuse_salt",
  "nextauth_secret": "$nextauth_secret",
  "encryption_key": "$encryption_key",
  "postgres_password": "$postgres_password",
  "clickhouse_password": "$clickhouse_password",
  "redis_password": "$redis_password",
  "s3_root_user": "$s3_root_user",
  "s3_root_password": "$s3_root_password"
}
EOF
)

    # Store secrets in AWS Secrets Manager
    local secret_arn=$(aws secretsmanager create-secret \
        --name "agentic-ptfm-langfuse" \
        --description "Langfuse deployment secrets" \
        --secret-string "$secrets_json" \
        --query 'ARN' \
        --output text)
    
    log_success "Secrets stored in AWS Secrets Manager:"
    log_info "  • Secret Name: agentic-ptfm-langfuse"
    log_info "  • ARN: $secret_arn"
    log_info "  • To retrieve: aws secretsmanager get-secret-value --secret-id agentic-ptfm-langfuse"
}

# Function to add Helm repository
add_helm_repo() {
    log_info "Adding Langfuse Helm repository..."
    
    helm repo add "$CHART_REPO" https://langfuse.github.io/langfuse-k8s
    helm repo update
    
    log_success "Helm repository added and updated."
}

# Function to deploy Langfuse
deploy_langfuse() {
    log_info "Deploying Langfuse to EKS cluster..."
    
    # Check if release already exists
    if helm list -n "$NAMESPACE" | grep -q "$RELEASE_NAME"; then
        log_warning "Release '$RELEASE_NAME' already exists. Upgrading..."
        helm upgrade "$RELEASE_NAME" "$CHART_NAME" \
            --namespace "$NAMESPACE" \
            --values "$VALUES_FILE"
        log_success "Langfuse upgrade initiated!"
    else
        log_info "Installing new Langfuse release..."
        helm install "$RELEASE_NAME" "$CHART_NAME" \
            --namespace "$NAMESPACE" \
            --values "$VALUES_FILE"
        log_success "Langfuse installation initiated!"
    fi
}

# Function to show access instructions
show_access_instructions() {
    echo
    log_success "🎉 Langfuse deployment has been initiated!"
    echo "Check status: kubectl get pods -n $NAMESPACE"
    echo "Port-forward: kubectl port-forward svc/langfuse-web -n $NAMESPACE 3000:3000"
    echo "Secrets stored in AWS Secrets Manager:"
    echo "  • Secret Name: agentic-ptfm-langfuse"
    echo "  • To retrieve: aws secretsmanager get-secret-value --secret-id agentic-ptfm-langfuse"
}

# Main deployment function
main() {
    echo "🚀 Langfuse EKS Deployment Script"
    echo "=========================================================="
    echo "⚠️  WARNING: This configuration uses minimal resources for testing only!"
    echo "⚠️  You will want to increase the resources for production workloads!"
    echo
    
    check_prerequisites
    create_namespace
    create_secrets
    add_helm_repo
    deploy_langfuse
    show_access_instructions
    
    echo
    log_success "✅ Deployment initiated successfully!"
    log_info "Check deployment status with: kubectl get pods -n $NAMESPACE"
}

# Script options
case "${1:-}" in
    --cleanup)
        log_info "Cleaning up Langfuse deployment..."
        helm uninstall "$RELEASE_NAME" -n "$NAMESPACE" --ignore-not-found
        kubectl delete secret langfuse-general langfuse-postgresql-auth langfuse-clickhouse-auth langfuse-redis-auth langfuse-s3-auth -n "$NAMESPACE" --ignore-not-found
        kubectl delete namespace "$NAMESPACE" --ignore-not-found
        aws secretsmanager delete-secret --secret-id "agentic-ptfm-langfuse" --force-delete-without-recovery
        log_success "Cleanup completed!"
        ;;
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --cleanup    Remove Langfuse deployment and clean up resources"
        echo "  --help, -h   Show this help message"
        echo
        echo "Default: Deploy Langfuse to EKS cluster with minimal testing configuration"
        echo
        echo "Resource Requirements (Testing Configuration):"
        echo "  • Total CPU Requests: ~900m"
        echo "  • Total CPU Limits: ~1.9 cores"
        echo "  • Total Memory Requests: ~2.5Gi"
        echo "  • Total Memory Limits: ~4.5Gi"
        echo "  • Total Storage: ~27Gi"
        echo
        ;;
    *)
        main
        ;;
esac