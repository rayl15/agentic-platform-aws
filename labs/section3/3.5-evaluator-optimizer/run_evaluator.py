#!/usr/bin/env python3
"""Run the Evaluator-Optimizer workflow - Iterative Answer Refinement."""

import sys
import boto3
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, START, END

# ─── Setup ───────────────────────────────────────────────────────────────────

session = boto3.Session()
bedrock = session.client(service_name="bedrock-runtime")

# Haiku for all calls (fast iteration)
HAIKU_MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# Maximum improvement iterations
MAX_ITERATIONS = 2

# ─── Simulated RAG Context ───────────────────────────────────────────────────
# In production, this would come from a vector store like OpenSearch or ChromaDB

OPENSEARCH_DOCS = """
## OpenSearch Cluster Health

Red status indicates at least one primary shard is not allocated.
Yellow status means all primaries are allocated but some replicas are not.
Green status means all shards are properly allocated.

## Common Causes of Red Health

1. **Disk Space**: Nodes may reject writes when disk usage exceeds 85%
2. **Memory Pressure**: JVM heap pressure above 75% causes GC issues
3. **Unassigned Shards**: Check _cat/shards?v&h=index,shard,prirep,state,unassigned.reason
4. **Node Failures**: Verify all nodes are connected with _cat/nodes

## Resolution Steps

1. Check cluster health: GET _cluster/health
2. Identify unassigned shards: GET _cat/shards?v&h=index,shard,prirep,state,unassigned.reason
3. Check disk space: GET _cat/allocation?v
4. Review node status: GET _cat/nodes?v
5. For disk issues: Clear old indices or add storage
6. For memory: Increase heap or reduce shard count
"""


# ─── Prompt Templates ────────────────────────────────────────────────────────

class BasePrompt(BaseModel):
    system_prompt: str
    user_prompt: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    model_id: str = HAIKU_MODEL_ID
    hyperparams: Dict[str, Any] = Field(default_factory=lambda: {"temperature": 0.5, "maxTokens": 1500})

    def __init__(self, **data):
        super().__init__(**data)
        if self.inputs:
            self.system_prompt = self.system_prompt.format(**self.inputs)
            self.user_prompt = self.user_prompt.format(**self.inputs)


class GeneratePrompt(BasePrompt):
    """Generates initial solution using context."""
    system_prompt: str = "You are an expert OpenSearch troubleshooter."
    user_prompt: str = """Provide a troubleshooting solution for this OpenSearch issue:

<question>{question}</question>

<documentation>
{context}
</documentation>

Include root causes, diagnostic steps, and resolution instructions.
Keep response under 150 words."""


class EvaluatePrompt(BasePrompt):
    """Evaluates the quality of the answer."""
    system_prompt: str = "You are a technical reviewer who provides constructive feedback."
    user_prompt: str = """Evaluate this OpenSearch troubleshooting solution:

<question>{question}</question>

<answer>{answer}</answer>

Assess completeness, accuracy, and clarity.
Provide 2-3 specific improvement suggestions.
Keep feedback under 100 words."""


class DecisionPrompt(BasePrompt):
    """Decides whether to improve or finalize."""
    system_prompt: str = "You make clear binary decisions."
    user_prompt: str = """Based on this feedback, does the solution need significant improvement?

<feedback>{feedback}</feedback>

Reply with ONLY 'IMPROVE' or 'DONE'.
- IMPROVE: If feedback identifies important gaps or errors
- DONE: If feedback is minor polish or solution is adequate"""


class ImprovePrompt(BasePrompt):
    """Improves the answer based on feedback."""
    system_prompt: str = "You are an expert OpenSearch troubleshooter who refines solutions."
    user_prompt: str = """Improve this solution based on feedback:

<question>{question}</question>

<current_solution>{answer}</current_solution>

<feedback>{feedback}</feedback>

<documentation>
{context}
</documentation>

Address all feedback points. Keep response under 150 words."""


# ─── Helper Functions ────────────────────────────────────────────────────────

def call_bedrock(prompt: BasePrompt) -> str:
    response = bedrock.converse(
        modelId=prompt.model_id,
        inferenceConfig=prompt.hyperparams,
        messages=[{"role": "user", "content": [{"text": prompt.user_prompt}]}],
        system=[{"text": prompt.system_prompt}],
    )
    return response["output"]["message"]["content"][0]["text"]


def log_step(step_name: str, detail: str = ""):
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    if detail:
        print(f"[{timestamp}] {step_name}: {detail}")
    else:
        print(f"[{timestamp}] {step_name}")


# ─── State Definition ────────────────────────────────────────────────────────

class EvaluatorState(TypedDict):
    """Workflow state for evaluator-optimizer pattern."""
    question: str
    context: str
    answer: str
    feedback: str
    iteration: int
    final_answer: str


# ─── Node Functions ──────────────────────────────────────────────────────────

def generate_answer(state: EvaluatorState) -> EvaluatorState:
    """Generate initial answer using RAG context."""
    log_step("📝 Generate", "Creating initial solution...")

    prompt = GeneratePrompt(inputs={
        "question": state["question"],
        "context": state["context"]
    })
    answer = call_bedrock(prompt)

    log_step("✅ Generated", f"Initial solution ({len(answer)} chars)")

    return {
        **state,
        "answer": answer,
        "iteration": 1
    }


def evaluate_answer(state: EvaluatorState) -> EvaluatorState:
    """Evaluate the current answer quality."""
    log_step("🔍 Evaluate", f"Iteration {state['iteration']}")

    prompt = EvaluatePrompt(inputs={
        "question": state["question"],
        "answer": state["answer"]
    })
    feedback = call_bedrock(prompt)

    # Show truncated feedback
    feedback_preview = feedback[:80].replace('\n', ' ') + "..."
    log_step("📋 Feedback", feedback_preview)

    return {
        **state,
        "feedback": feedback
    }


def should_improve(state: EvaluatorState) -> str:
    """Decide: IMPROVE or DONE based on feedback and iteration count."""

    # Hard limit on iterations
    if state["iteration"] >= MAX_ITERATIONS:
        log_step("🛑 Max iterations", f"Reached limit of {MAX_ITERATIONS}")
        return "DONE"

    # Ask LLM to decide
    prompt = DecisionPrompt(inputs={"feedback": state["feedback"]})
    decision = call_bedrock(prompt).strip().upper()

    # Parse decision
    if "IMPROVE" in decision:
        log_step("🔄 Decision", "IMPROVE - Refining solution")
        return "IMPROVE"
    else:
        log_step("✓ Decision", "DONE - Solution is adequate")
        return "DONE"


def improve_answer(state: EvaluatorState) -> EvaluatorState:
    """Improve the answer based on feedback."""
    log_step("🔧 Improve", "Refining based on feedback...")

    prompt = ImprovePrompt(inputs={
        "question": state["question"],
        "answer": state["answer"],
        "feedback": state["feedback"],
        "context": state["context"]
    })
    improved = call_bedrock(prompt)

    log_step("✅ Improved", f"Refined solution ({len(improved)} chars)")

    return {
        **state,
        "answer": improved,
        "iteration": state["iteration"] + 1
    }


def finalize_answer(state: EvaluatorState) -> EvaluatorState:
    """Finalize the answer."""
    log_step("🏁 Finalize", f"Complete after {state['iteration']} iteration(s)")

    return {
        **state,
        "final_answer": state["answer"]
    }


# ─── Build Graph ─────────────────────────────────────────────────────────────

def create_evaluator_workflow() -> StateGraph:
    workflow = StateGraph(EvaluatorState)

    # Add nodes
    workflow.add_node("generate", generate_answer)
    workflow.add_node("evaluate", evaluate_answer)
    workflow.add_node("improve", improve_answer)
    workflow.add_node("finalize", finalize_answer)

    # Linear flow: START → generate → evaluate
    workflow.add_edge(START, "generate")
    workflow.add_edge("generate", "evaluate")

    # Conditional: evaluate → improve OR finalize
    workflow.add_conditional_edges(
        "evaluate",
        should_improve,
        {"IMPROVE": "improve", "DONE": "finalize"}
    )

    # Loop: improve → evaluate (for re-evaluation)
    workflow.add_edge("improve", "evaluate")

    # End: finalize → END
    workflow.add_edge("finalize", END)

    return workflow.compile()


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "OpenSearch cluster showing red health status and not responding to queries"

    print()
    print("🔄 Evaluator-Optimizer: Iterative Answer Refinement")
    print("=" * 55)
    print(f"Question: {question}")
    print(f"Max iterations: {MAX_ITERATIONS}")
    print("=" * 55)
    print()

    start_time = datetime.now()

    graph = create_evaluator_workflow()
    initial_state = EvaluatorState(
        question=question,
        context=OPENSEARCH_DOCS,
        answer="",
        feedback="",
        iteration=0,
        final_answer=""
    )

    result = graph.invoke(initial_state)

    elapsed = (datetime.now() - start_time).total_seconds()

    print()
    print("=" * 55)
    print(f"⏱️  Total time: {elapsed:.2f}s")
    print(f"🔄 Iterations: {result['iteration']}")
    print("=" * 55)
    print()
    print("📋 FINAL SOLUTION")
    print("-" * 55)
    print(result["final_answer"])
