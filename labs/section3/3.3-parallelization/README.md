# 3.3 Parallelization

Run multiple LLM calls simultaneously to reduce latency.

## Quick Start

```bash
# Ensure dependencies are installed (from section root)
# Then run the parallel workflow

python3 run_parallel.py "How to scale OpenSearch clusters effectively?"
python3 run_parallel.py "What's the best way to secure OpenSearch?"
python3 run_parallel.py "How do I optimize query performance?"
```

## What You'll Learn

- Fan-out: dispatch to multiple parallel workers
- Fan-in: collect and merge results
- LangGraph's parallel edge syntax
- When parallelization beats sequential execution

## Files

| File | Description |
|------|-------------|
| `run_parallel.py` | Multi-aspect solution generator (3 parallel LLM calls) |
| `bonus-notebook.ipynb` | Deep-dive with visualizations |

## The Parallel Flow

```
                ┌──────────┐
                │  START   │
                └────┬─────┘
                     │
              ┌──────┴──────┐
              │ Parallelizer │
              └──────┬──────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │Beginner │ │ Expert  │ │  Cost   │
   └────┬────┘ └────┬────┘ └────┬────┘
        │            │            │
        └────────────┼────────────┘
                     ▼
              ┌──────────┐
              │  Format  │
              └────┬─────┘
                   │
                   ▼
              ┌──────────┐
              │   END    │
              └──────────┘
```

## Three Solution Aspects

| Aspect | Focus |
|--------|-------|
| `Beginner` | Step-by-step, basic concepts, defaults |
| `Expert` | Advanced configs, optimizations, edge cases |
| `Cost` | Resource efficiency, cost tradeoffs |

## Key LangGraph Pattern

```python
# Fan-out: one node to many
workflow.add_edge("parallelizer", "beginner")
workflow.add_edge("parallelizer", "expert")
workflow.add_edge("parallelizer", "cost")

# Fan-in: many nodes to one (waits for ALL to complete)
workflow.add_edge(["beginner", "expert", "cost"], "format")
```

## When to Use Parallelization

- Independent subtasks with no dependencies
- Multiple perspectives improve the result
- Latency reduction is critical
- Each task needs focused attention

## When NOT to Use

- Tasks depend on each other's output
- Sequential ordering matters
- Resource constraints (API rate limits)
- Simple queries that don't benefit from multiple perspectives
