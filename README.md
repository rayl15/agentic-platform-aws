# Agentic Platform on AWS

A production-ready platform for deploying agentic AI systems on AWS. This repository is the companion code for the Udemy course **"Agentic AI Engineering on AWS"**.

## What You'll Build

This platform demonstrates how to operationalize AI agents at scale:

- **Multiple Agent Types**: Chat, RAG, Jira integration, and more
- **Gateway Pattern**: LLM Gateway, Memory Gateway, Retrieval Gateway
- **Production Infrastructure**: EKS, Cognito, Aurora PostgreSQL, OpenSearch
- **Observability**: OpenTelemetry, X-Ray traces, CloudWatch metrics
- **Security**: IRSA, JWT authentication, least-privilege access

## Prerequisites

Before starting, ensure you have:

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Platform code uses modern Python features |
| Docker Desktop | Latest | Local development services |
| AWS Account | With Bedrock access | Model inference (Claude, etc.) |
| Git | Latest | Clone this repository |
| uv | Latest | Fast Python package manager |

## Quick Start (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/rayl15/agentic-platform-aws.git
cd agentic-platform-aws
```

### 2. Start Local Services

```bash
docker compose up -d
```

This starts:
- **PostgreSQL** (port 5432) - Memory Gateway database with pgvector
- **Redis** (port 6379) - Caching and rate limiting
- **LiteLLM** (port 4000) - LLM Gateway for model routing

### 3. Install Dependencies

```bash
make install
```

### 4. Configure Environment

```bash
make setup-env
```

This creates `.env` at the repo root and a `.env` for each agent from the shipped `.env.example` templates. Edit the root `.env` to set your AWS region if Bedrock is enabled elsewhere:
```
AWS_REGION=us-east-1
```

### 5. Run Your First Agent

```bash
make dev-agentic-chat
```

### 6. Test It

> The lesson 1.2 video shows a simplified conceptual payload. The actual API uses structured content blocks — the same schema you'll see in the deployed demo (Lesson 8.1) and multi-agent labs.

```bash
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "message": {"role": "user", "content": [{"type": "text", "text": "Hello, who are you?"}]},
    "session_id": "local-dev"
  }'
```

You should see a JSON response from the agent.

## Project Structure

```
├── src/
│   ├── agents/              # Individual agent implementations
│   │   ├── agentic_chat/    # Basic conversational agent
│   │   ├── agentic_rag/     # RAG-powered agent
│   │   └── jira_agent/      # Jira integration agent
│   ├── services/            # Gateway microservices
│   │   ├── llm_gateway/     # Routes LLM requests to providers
│   │   ├── memory_gateway/  # Conversation history & embeddings
│   │   └── retrieval_gateway/ # Knowledge base queries
│   └── agentic_platform/    # Shared core library
├── infrastructure/          # Terraform modules for AWS deployment
├── labs/                    # Hands-on learning modules
└── docker-compose.yaml      # Local development services
```

## Architecture

### Agent Design Pattern

Each agent runs as an independent FastAPI server that:
- Connects to gateways (LLM, Memory, Retrieval) via authenticated requests
- Uses a shared core library for consistent patterns
- Emits telemetry via OpenTelemetry

### Gateway Pattern Benefits

- **Abstraction**: Agents don't know about underlying providers
- **Security**: Gateways hold IAM roles, not agents
- **Flexibility**: Swap providers without changing agent code
- **Observability**: Centralized logging and metrics


## AWS Deployment

**Note**: Deploying to AWS will incur costs. The infrastructure includes EKS, Aurora, OpenSearch, and other services.

## Course

This repository accompanies the Udemy course **"Agentic AI Engineering on AWS"**.

The course covers:
- Setting up your local development environment
- Understanding the platform architecture
- Building agents with different frameworks (Strands, LangGraph)
- Deploying to production on AWS
- Monitoring and observability
- Security best practices

## License

This project is licensed under the MIT-0 License. See [LICENSE](LICENSE) for details.

## Acknowledgments

This project builds upon patterns and practices from the AWS community. Special thanks to the original contributors at AWS for the foundational architecture.
