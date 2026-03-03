# 3.4 Orchestrator-Worker Pattern

Dynamic task delegation where an LLM plans what workers to spawn at runtime.

## Quick Start

```bash
python3 run_orchestrator.py "OpenSearch cluster showing red health status"
python3 run_orchestrator.py "Slow query performance on large indices"
python3 run_orchestrator.py "High memory usage causing node crashes"
```

## What You'll Learn

- Dynamic task planning with LLM orchestrator
- LangGraph `Send` API for runtime worker creation
- `operator.add` for aggregating parallel results
- Conditional edges for dynamic dispatch

## Key Difference from Parallelization (3.3)

| Parallelization | Orchestrator-Worker |
|-----------------|---------------------|
| Tasks known ahead of time | Tasks determined at runtime |
| Fixed number of workers | Dynamic number of workers |
| `add_edge(["a", "b", "c"], "join")` | `Send("worker", {task})` |

## Files

| File | Description |
|------|-------------|
| `run_orchestrator.py` | Dynamic troubleshooting system |
| `bonus-notebook.ipynb` | Deep-dive with RAG integration |

## The Orchestrator Flow

```
                ┌──────────┐
                │  START   │
                └────┬─────┘
                     │
              ┌──────┴──────┐
              │    Plan     │  ← Orchestrator decides tasks
              │ (Haiku 4.5) │
              └──────┬──────┘
                     │
          ┌──────────┼──────────┐  ← Dynamic dispatch
          ▼          ▼          ▼     (Send API)
     ┌─────────┐┌─────────┐┌─────────┐
     │Worker 1 ││Worker 2 ││Worker N │  ← N workers
     │(Nova µ) ││(Nova µ) ││(Nova µ) │     created at runtime
     └────┬────┘└────┬────┘└────┬────┘
          │          │          │
          └──────────┼──────────┘  ← operator.add
                     ▼               aggregates results
              ┌──────────┐
              │Synthesize│  ← Combines findings
              │(Haiku 4.5)│
              └────┬─────┘
                   │
                   ▼
              ┌──────────┐
              │   END    │
              └──────────┘
```

## Key LangGraph Patterns

### 1. Send API (Dynamic Worker Creation)

```python
from langgraph.constants import Send

def assign_workers(state):
    """Create N workers at runtime based on orchestrator's plan."""
    return [
        Send("investigate", {"issue": issue})
        for issue in state["diagnostic_plan"]  # Dynamic!
    ]

# Connect with conditional edges
workflow.add_conditional_edges("plan", assign_workers, ["investigate"])
```

### 2. Result Aggregation with operator.add

```python
from typing import Annotated
import operator

class OrchestratorState(TypedDict):
    problem: str
    diagnostic_plan: List[str]
    # operator.add aggregates results from all parallel workers
    investigation_results: Annotated[List[Dict], operator.add]
    final_report: str
```

### 3. Worker State (Separate from Main State)

```python
class WorkerState(TypedDict):
    """Each worker gets its own state slice."""
    problem: str
    issue: str  # The specific task assigned
    investigation_results: Annotated[List[Dict], operator.add]
```

## Model Selection Strategy

| Role | Model | Why |
|------|-------|-----|
| Orchestrator (Plan) | Haiku 4.5 | Needs reasoning for task decomposition |
| Workers | Nova Micro | Fast execution, simple focused tasks |
| Synthesizer | Haiku 4.5 | Needs reasoning to combine findings |

## When to Use Orchestrator-Worker

✅ **Good fit:**
- Can't predict subtasks ahead of time
- Task decomposition requires LLM reasoning
- Complex problems needing investigation
- Variable number of parallel operations

❌ **Use Parallelization instead when:**
- Tasks are known upfront
- Fixed number of perspectives needed
- Simple fan-out/fan-in pattern

## Example Output

```
🎭 Orchestrator-Worker: Dynamic Task Delegation
=======================================================
Problem: OpenSearch cluster showing red health status
=======================================================

[09:45:12.481] 🎯 Orchestrator: Planning diagnostic steps...
[09:45:14.892] 📋 Plan created: 3 tasks identified
    Task 1: Unassigned shards due to disk space issues...
    Task 2: Node connectivity problems causing cluster...
    Task 3: Index corruption from improper shutdown...
[09:45:14.893] 🚀 Dispatching workers: 3 parallel tasks
[09:45:14.895] 🔍 Worker started: Unassigned shards...
[09:45:14.896] 🔍 Worker started: Node connectivity...
[09:45:14.897] 🔍 Worker started: Index corruption...
[09:45:17.234] ✅ Worker completed: Node connectivity...
[09:45:17.891] ✅ Worker completed: Unassigned shards...
[09:45:18.102] ✅ Worker completed: Index corruption...
[09:45:18.103] 📝 Synthesizer: Combining findings...
[09:45:21.456] ✅ Synthesis complete

=======================================================
⏱️  Total time: 8.98s
📊 Tasks planned: 3
📊 Workers executed: 3
=======================================================
```
