# 3.2 Intelligent Routing

Direct requests to specialized handlers based on LLM classification.

## Quick Start

```bash
# Ensure ChromaDB is set up (from 3.1)
# Then run the routing workflow

python3 run_routing.py "How do I install OpenSearch on AWS?"
python3 run_routing.py "What's the best way to implement role-based access control?"
python3 run_routing.py "How can I write efficient fuzzy match queries?"
python3 run_routing.py "What's the optimal shard size for large indices?"
```

## What You'll Learn

- Use an LLM to classify inputs into categories
- Route requests to specialized handlers
- Use LangGraph conditional edges for branching
- When routing beats a single generic prompt

## Files

| File | Description |
|------|-------------|
| `run_routing.py` | Question classifier with 4 specialized handlers |
| `bonus-notebook.ipynb` | Deep-dive with visualizations |

## The Routing Flow

```
          ┌──────────┐
          │ Classify │
          └────┬─────┘
               │
    ┌──────┬───┴───┬──────┐
    ▼      ▼       ▼      ▼
INSTALL SECURITY QUERY  PERF
    │      │       │      │
    └──────┴───┬───┴──────┘
               ▼
           Response
```

## Categories

| Category | Handles |
|----------|---------|
| `INSTALL` | Installation, setup, cluster configuration |
| `SECURITY` | Authentication, access control, encryption |
| `QUERY` | Search syntax, indexing, query optimization |
| `PERFORMANCE` | Scaling, monitoring, resource management |

## When to Use Routing

- Different inputs need genuinely different handling
- A single generic prompt would be mediocre at everything
- You can reliably classify into distinct categories

## When NOT to Use

- Categories overlap heavily
- A single well-crafted prompt handles all cases
- Classification adds unnecessary latency
