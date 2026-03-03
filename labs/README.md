# Labs

Hands-on code for each course section. **Folder structure matches the video lessons exactly.**

## Structure

```
labs/
  section2/    # LLM Fundamentals (Lessons 2.1 - 2.4)
  section3/    # Agent Workflow Patterns (Lessons 3.1 - 3.5)
  section4/    # Building Production Agents (Lessons 4.1 - 4.5)
  section5/    # Multi-Agent Systems & MCP (Lessons 5.1 - 5.4)
  section6/    # Gateway Services (Lessons 6.1 - 6.3)
  section7/    # Infrastructure & Deployment (Lessons 7.1 - 7.5)
```

## How to Use

1. Watch the video lesson (e.g., "3.1 Prompt Chaining")
2. Navigate to the matching folder: `labs/section3/3.1-prompt-chaining/`
3. Run the Python scripts shown in the video
4. **Bonus notebooks** (`bonus-*.ipynb`) provide deeper exploration

## Prerequisites

Complete the local dev setup from Section 1:

```bash
# From repo root
docker compose up -d
uv sync && source .venv/bin/activate
```

## File Types

| File | Purpose |
|------|---------|
| `*.py` | Scripts shown in video demos - **run these** |
| `bonus-*.ipynb` | Optional deep-dive notebooks for experimentation |
| `README.md` | Lesson-specific instructions |

## Section Overview

### Section 2: LLM Fundamentals
- 2.1 Bedrock Converse API
- 2.2 Prompt Engineering (Chain of Thought, Few-Shot)
- 2.3 RAG Basics (Embeddings, Vector Search)
- 2.4 Function Calling & Tool Use

### Section 3: Agent Workflow Patterns
- 3.1 Prompt Chaining
- 3.2 Intelligent Routing
- 3.3 Parallelization
- 3.4 Orchestrator-Worker Pattern
- 3.5 Evaluator-Optimizer Loop

### Section 4: Building Production Agents
- 4.1 Platform Core (Models, Middleware, Gateway Clients)
- 4.2 Chat Agent with Strands
- 4.3 RAG Agent with Bedrock Knowledge Base
- 4.4 LangGraph Agent
- 4.5 Framework-Agnostic Abstractions

### Section 5: Multi-Agent Systems & MCP
- 5.1 Model Context Protocol (MCP)
- 5.2 Build an MCP Server
- 5.3 Multi-Agent Delegation
- 5.4 Jira Agent with MCP

### Section 6: Gateway Services
- 6.1 LLM Gateway (LiteLLM)
- 6.2 Memory Gateway
- 6.3 Retrieval Gateway

### Section 7: Infrastructure & Deployment
- 7.1 AWS Infrastructure with Terraform
- 7.2 EKS Cluster & Helm Charts
- 7.3 Security (Cognito, IRSA)
- 7.4 Observability (OpenTelemetry)
- 7.5 CI/CD (GitHub Actions)
