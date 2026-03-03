# 3.1 Prompt Chaining

Break complex tasks into sequential LLM calls, each building on the previous.

## Quick Start

```bash
# 1. Set up ChromaDB with OpenSearch docs (one-time)
python3 setup_chroma.py

# 2. Run the 4-step prompt chain
python3 run_prompt_chain.py "Explain OpenSearch's security configuration"
```

## What You'll Learn

- Break complex tasks into focused subtasks
- Pass state between sequential LLM calls
- Use LangGraph to define workflows
- Tradeoffs: accuracy vs latency

## Files

| File | Description |
|------|-------------|
| `setup_chroma.py` | Index OpenSearch docs into ChromaDB |
| `run_prompt_chain.py` | 4-step Documentation Explainer |
| `bonus-notebook.ipynb` | Deep-dive with visualizations |

## The 4-Step Pipeline

1. **Extract Concepts** - RAG retrieval + concept extraction
2. **Simplify Explanation** - Explain in simple terms
3. **Generate Examples** - Practical code examples
4. **Format Output** - Clean markdown document
