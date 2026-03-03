#!/usr/bin/env python3
"""Run the Parallelization workflow - Multi-Aspect Solution Generator."""

import sys
import boto3
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, START, END

# ─── Setup ───────────────────────────────────────────────────────────────────

session = boto3.Session()
bedrock = session.client(service_name="bedrock-runtime")

# Using Haiku 4.5 for fast parallel execution
HAIKU_MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# ─── Prompt Templates ────────────────────────────────────────────────────────

class BasePrompt(BaseModel):
    system_prompt: str
    user_prompt: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    model_id: str = HAIKU_MODEL_ID
    hyperparams: Dict[str, Any] = Field(default_factory=lambda: {"temperature": 0.5, "maxTokens": 1000})

    def __init__(self, **data):
        super().__init__(**data)
        if self.inputs:
            self.system_prompt = self.system_prompt.format(**self.inputs)
            self.user_prompt = self.user_prompt.format(**self.inputs)

SYSTEM_PROMPT = "You are a helpful assistant specializing in OpenSearch documentation and support."

class BeginnerPrompt(BasePrompt):
    system_prompt: str = SYSTEM_PROMPT
    user_prompt: str = """Create a beginner-friendly solution for this OpenSearch question:
{question}

Focus on:
- Simple, step-by-step instructions
- Basic concepts and terminology
- Common pitfalls to avoid
- Default configurations"""

class ExpertPrompt(BasePrompt):
    system_prompt: str = SYSTEM_PROMPT
    user_prompt: str = """Create an advanced, expert-level solution for this OpenSearch question:
{question}

Include:
- Advanced configurations
- Performance optimizations
- Best practices
- Edge cases and considerations"""

class CostPrompt(BasePrompt):
    system_prompt: str = SYSTEM_PROMPT
    user_prompt: str = """Create a cost-optimized solution for this OpenSearch question:
{question}

Focus on:
- Resource efficiency
- Infrastructure costs
- Performance/cost tradeoffs
- Cost monitoring and optimization"""

# ─── Helper Functions ────────────────────────────────────────────────────────

def call_bedrock(prompt: BasePrompt) -> str:
    response = bedrock.converse(
        modelId=prompt.model_id,
        inferenceConfig=prompt.hyperparams,
        messages=[{"role": "user", "content": [{"text": prompt.user_prompt}]}],
        system=[{"text": prompt.system_prompt}],
    )
    return response["output"]["message"]["content"][0]["text"]

def log_execution(func_name: str):
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Starting {func_name}")

# ─── State & Nodes ───────────────────────────────────────────────────────────

class WorkflowState(TypedDict):
    question: str
    beginner_solution: str
    expert_solution: str
    cost_solution: str
    final_output: str

def parallel_start(state: WorkflowState) -> WorkflowState:
    """Entry point - fans out to parallel workers."""
    return state

def generate_beginner_solution(state: WorkflowState) -> Dict[str, str]:
    """Generates a beginner-friendly solution."""
    log_execution("beginner_solution")
    prompt = BeginnerPrompt(inputs={"question": state["question"]})
    solution = call_bedrock(prompt)
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] ✅ Completed beginner_solution")
    return {"beginner_solution": solution}

def generate_expert_solution(state: WorkflowState) -> Dict[str, str]:
    """Generates an expert-level solution."""
    log_execution("expert_solution")
    prompt = ExpertPrompt(inputs={"question": state["question"]})
    solution = call_bedrock(prompt)
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] ✅ Completed expert_solution")
    return {"expert_solution": solution}

def generate_cost_solution(state: WorkflowState) -> Dict[str, str]:
    """Generates a cost-optimized solution."""
    log_execution("cost_solution")
    prompt = CostPrompt(inputs={"question": state["question"]})
    solution = call_bedrock(prompt)
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] ✅ Completed cost_solution")
    return {"cost_solution": solution}

def format_output(state: WorkflowState) -> WorkflowState:
    """Joins parallel results into final output."""
    state["final_output"] = f"""
# OpenSearch Solution Approaches

## 📘 Beginner-Friendly Solution
{state["beginner_solution"]}

## 🎯 Expert-Level Solution
{state["expert_solution"]}

## 💰 Cost-Optimized Solution
{state["cost_solution"]}
"""
    return state

# ─── Build Graph ─────────────────────────────────────────────────────────────

def create_parallel_workflow() -> StateGraph:
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("parallelizer", parallel_start)
    workflow.add_node("beginner", generate_beginner_solution)
    workflow.add_node("expert", generate_expert_solution)
    workflow.add_node("cost", generate_cost_solution)
    workflow.add_node("format", format_output)

    # Fan-out: parallelizer → 3 parallel workers
    workflow.add_edge(START, "parallelizer")
    workflow.add_edge("parallelizer", "beginner")
    workflow.add_edge("parallelizer", "expert")
    workflow.add_edge("parallelizer", "cost")

    # Fan-in: all 3 workers → format (waits for all to complete)
    workflow.add_edge(["beginner", "expert", "cost"], "format")

    # End
    workflow.add_edge("format", END)

    return workflow.compile()

# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "How to scale OpenSearch clusters effectively?"

    print()
    print("⚡ Parallelization: Multi-Aspect Solution Generator")
    print("=" * 55)
    print(f"Question: {question}")
    print("=" * 55)
    print()
    print("Running 3 LLM calls in parallel...")
    print()

    start_time = datetime.now()

    graph = create_parallel_workflow()
    state = WorkflowState(
        question=question,
        beginner_solution="",
        expert_solution="",
        cost_solution="",
        final_output=""
    )
    result = graph.invoke(state)

    elapsed = (datetime.now() - start_time).total_seconds()

    print()
    print("=" * 55)
    print(f"⏱️  Total time: {elapsed:.2f}s (parallel execution)")
    print("=" * 55)
    print(result["final_output"])
