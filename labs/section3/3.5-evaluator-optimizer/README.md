# Lesson 3.5 — Evaluator-Optimizer Pattern

Iterative answer refinement through feedback loops.

## What You'll Learn

- How to evaluate LLM outputs programmatically
- Implementing improvement loops with conditional edges
- Setting iteration limits to control compute costs
- When iterative refinement adds value vs. overhead

## The Pattern

```
Generate → Evaluate → Decide → [Improve → Evaluate]* → Finalize
                        ↓
                  DONE or IMPROVE
```

Key insight: An LLM evaluates its own output and provides feedback for improvement.

## Run the Demo

```bash
# From this folder
PYTHONUNBUFFERED=1 python3 -u run_evaluator.py

# With custom question
python3 run_evaluator.py "OpenSearch indexing is slow"
```

## Expected Output

```
🔄 Evaluator-Optimizer: Iterative Answer Refinement
=======================================================
Question: OpenSearch cluster showing red health status...
Max iterations: 2
=======================================================

[...] 📝 Generate: Creating initial solution...
[...] ✅ Generated: Initial solution (858 chars)
[...] 🔍 Evaluate: Iteration 1
[...] 📋 Feedback: # Technical Review...
[...] 🔄 Decision: IMPROVE - Refining solution
[...] 🔧 Improve: Refining based on feedback...
[...] ✅ Improved: Refined solution (1006 chars)
[...] 🔍 Evaluate: Iteration 2
[...] 🛑 Max iterations: Reached limit of 2
[...] 🏁 Finalize: Complete after 2 iteration(s)

⏱️  Total time: ~18s
🔄 Iterations: 2
```

## Key Code Concepts

### 1. State with Iteration Counter

```python
class EvaluatorState(TypedDict):
    question: str
    answer: str
    feedback: str
    iteration: int      # Track loop count
    final_answer: str
```

### 2. Conditional Edge for Loop Control

```python
workflow.add_conditional_edges(
    "evaluate",
    should_improve,  # Returns "IMPROVE" or "DONE"
    {"IMPROVE": "improve", "DONE": "finalize"}
)

# Loop back: improve → evaluate
workflow.add_edge("improve", "evaluate")
```

### 3. Decision Function with Max Iterations

```python
def should_improve(state: EvaluatorState) -> str:
    if state["iteration"] >= MAX_ITERATIONS:
        return "DONE"  # Hard limit

    # Ask LLM to decide based on feedback quality
    decision = call_bedrock(DecisionPrompt(...))
    return "IMPROVE" if "IMPROVE" in decision else "DONE"
```

## When to Use This Pattern

**Good fit:**
- Clear evaluation criteria exist
- Quality improvement is measurable
- Extra latency is acceptable
- High-stakes outputs (legal, medical, code)

**Avoid when:**
- Simple factual queries
- Real-time requirements
- Evaluation criteria are subjective
- Diminishing returns after first pass

## Files

| File | Description |
|------|-------------|
| `run_evaluator.py` | Standalone demo script |
| `bonus-notebook.ipynb` | Deep-dive with RAG integration |
