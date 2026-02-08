# Agentic Platform on AWS

A production-ready platform for deploying agentic AI systems on AWS. This repository is the companion code for the Udemy course **"Building Production Agentic AI Platforms on AWS"**.

![Platform Architecture](media/highlevel-architecture.png)

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
cp .env.example .env
```

Edit `.env` and set your AWS region (ensure Bedrock is enabled):
```
AWS_REGION=us-east-1
```

### 5. Run Your First Agent

```bash
make dev agentic_chat
```

### 6. Test It

```bash
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, who are you?"}'
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

![Agent Architecture](media/agent-design.png)

Each agent runs as an independent FastAPI server that:
- Connects to gateways (LLM, Memory, Retrieval) via authenticated requests
- Uses a shared core library for consistent patterns
- Emits telemetry via OpenTelemetry

### Gateway Pattern Benefits

- **Abstraction**: Agents don't know about underlying providers
- **Security**: Gateways hold IAM roles, not agents
- **Flexibility**: Swap providers without changing agent code
- **Observability**: Centralized logging and metrics

## Labs

Five progressive modules to deepen your understanding:

1. **Module 1**: Prompt Engineering & Evaluation
2. **Module 2**: Common Agentic Patterns
3. **Module 3**: Building Agentic Applications
4. **Module 4**: Advanced Concepts (Multi-Agent, MCP, AgentCore)
5. **Module 5**: Deployment and Infrastructure

Run labs locally:
```bash
uv run jupyter lab
```

## AWS Deployment

For production deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

**Note**: Deploying to AWS will incur costs. The infrastructure includes EKS, Aurora, OpenSearch, and other services.

## Course

This repository accompanies the Udemy course **"Building Production Agentic AI Platforms on AWS"**.

The course covers:
- Setting up your local development environment
- Understanding the platform architecture
- Building agents with different frameworks (Strands, LangGraph, CrewAI)
- Deploying to production on AWS
- Monitoring and observability
- Security best practices

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT-0 License. See [LICENSE](LICENSE) for details.

## Acknowledgments

This project builds upon patterns and practices from the AWS community. Special thanks to the original contributors at AWS for the foundational architecture.
