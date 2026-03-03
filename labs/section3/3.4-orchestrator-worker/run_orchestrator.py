#!/usr/bin/env python3
"""Run the Orchestrator-Worker workflow - Dynamic Task Delegation."""

import sys
import boto3
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, Any, List, TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

# ─── Setup ───────────────────────────────────────────────────────────────────

session = boto3.Session()
bedrock = session.client(service_name="bedrock-runtime")

# Haiku 4.5 for orchestrator (planning + synthesis)
HAIKU_MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# Nova Micro for workers (fast parallel execution)
NOVA_MICRO_MODEL_ID = "us.amazon.nova-micro-v1:0"

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


class PlanningPrompt(BasePrompt):
    """Orchestrator: Plans diagnostic steps dynamically."""
    system_prompt: str = "You are an expert OpenSearch diagnostician. Identify potential causes for issues. Be concise."
    user_prompt: str = """Plan the diagnostic steps for this OpenSearch issue:
{problem}

Return EXACTLY 3 potential causes, one per line.
Each line should be SHORT (under 50 chars) and specific.
Example format:
Unassigned shards due to disk space
Node connectivity failure
Index corruption from improper shutdown

Do NOT use markdown, bullets, or numbering. Just plain text, one cause per line."""


class InvestigationPrompt(BasePrompt):
    """Worker: Investigates a specific issue (uses Nova Micro for speed)."""
    model_id: str = NOVA_MICRO_MODEL_ID
    system_prompt: str = "You are an expert OpenSearch troubleshooter."
    user_prompt: str = """Investigate this potential cause of an OpenSearch problem:

Problem: {problem}
Potential Cause: {issue}

Provide:
1. How to diagnose if this is the actual cause
2. Expected symptoms
3. Resolution steps
4. Prevention measures

Keep response concise (under 200 words)."""


class SynthesisPrompt(BasePrompt):
    """Synthesizer: Combines all worker findings into final report."""
    system_prompt: str = "You are an expert OpenSearch engineer. Create comprehensive troubleshooting reports."
    user_prompt: str = """Create a troubleshooting report for this OpenSearch issue:
{problem}

Investigation findings:
{issues_summary}

Synthesize into:
1. Most likely root causes (ranked)
2. Recommended resolution approach
3. Verification steps"""


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


# ─── State Definitions ───────────────────────────────────────────────────────

class OrchestratorState(TypedDict):
    """Main workflow state."""
    problem: str
    diagnostic_plan: List[str]
    investigation_results: Annotated[List[Dict[str, str]], operator.add]  # Aggregates worker results
    final_report: str


class WorkerState(TypedDict):
    """Worker-specific state."""
    problem: str
    issue: str
    investigation_results: Annotated[List[Dict[str, str]], operator.add]


# ─── Node Functions ──────────────────────────────────────────────────────────

def plan_diagnostics(state: OrchestratorState) -> OrchestratorState:
    """Orchestrator: Plans what tasks to delegate to workers."""
    log_step("🎯 Orchestrator", "Planning diagnostic steps...")

    prompt = PlanningPrompt(inputs={"problem": state["problem"]})
    plan = call_bedrock(prompt)

    # Extract each diagnostic step
    steps = [step.strip() for step in plan.split('\n') if step.strip() and len(step.strip()) > 10][:3]

    log_step("📋 Plan created", f"{len(steps)} tasks identified")
    for i, step in enumerate(steps, 1):
        print(f"    Task {i}: {step[:60]}...")

    return {
        **state,
        "diagnostic_plan": steps,
        "investigation_results": []
    }


def investigate_issue(state: WorkerState) -> WorkerState:
    """Worker: Investigates a specific issue assigned by orchestrator."""
    issue_short = state["issue"][:50] + "..." if len(state["issue"]) > 50 else state["issue"]
    log_step("🔍 Worker started", issue_short)

    prompt = InvestigationPrompt(inputs={
        "problem": state["problem"],
        "issue": state["issue"]
    })
    result = call_bedrock(prompt)

    log_step("✅ Worker completed", issue_short)

    return {
        "investigation_results": [{"issue": state["issue"], "result": result}]
    }


def synthesize_findings(state: OrchestratorState) -> OrchestratorState:
    """Synthesizer: Combines all worker results into final report."""
    log_step("📝 Synthesizer", "Combining findings...")

    # Format worker results
    issues_summary = ""
    for r in state["investigation_results"]:
        issues_summary += f"\n## {r['issue']}\n{r['result']}\n"

    prompt = SynthesisPrompt(inputs={
        "problem": state["problem"],
        "issues_summary": issues_summary
    })
    final_report = call_bedrock(prompt)

    log_step("✅ Synthesis complete")

    return {
        **state,
        "final_report": final_report
    }


# ─── Dynamic Worker Assignment ───────────────────────────────────────────────

def assign_workers(state: OrchestratorState):
    """Dynamically creates workers for each task in the plan.

    This is the key pattern! The Send API creates N workers at runtime
    based on what the orchestrator decided.
    """
    log_step("🚀 Dispatching workers", f"{len(state['diagnostic_plan'])} parallel tasks")

    return [
        Send("investigate", {"problem": state["problem"], "issue": issue})
        for issue in state["diagnostic_plan"]
    ]


# ─── Build Graph ─────────────────────────────────────────────────────────────

def create_orchestrator_workflow() -> StateGraph:
    workflow = StateGraph(OrchestratorState)

    # Add nodes
    workflow.add_node("plan", plan_diagnostics)
    workflow.add_node("investigate", investigate_issue)
    workflow.add_node("synthesize", synthesize_findings)

    # Orchestrator flow
    workflow.add_edge(START, "plan")

    # Dynamic dispatch: plan → N workers (via Send API)
    workflow.add_conditional_edges("plan", assign_workers, ["investigate"])

    # All workers → synthesizer (waits for all to complete)
    workflow.add_edge("investigate", "synthesize")

    workflow.add_edge("synthesize", END)

    return workflow.compile()


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    problem = sys.argv[1] if len(sys.argv) > 1 else "OpenSearch cluster showing red health status and not responding to queries"

    print()
    print("🎭 Orchestrator-Worker: Dynamic Task Delegation")
    print("=" * 55)
    print(f"Problem: {problem}")
    print("=" * 55)
    print()

    start_time = datetime.now()

    graph = create_orchestrator_workflow()
    initial_state = OrchestratorState(
        problem=problem,
        diagnostic_plan=[],
        investigation_results=[],
        final_report=""
    )

    result = graph.invoke(initial_state)

    elapsed = (datetime.now() - start_time).total_seconds()

    print()
    print("=" * 55)
    print(f"⏱️  Total time: {elapsed:.2f}s")
    print(f"📊 Tasks planned: {len(result['diagnostic_plan'])}")
    print(f"📊 Workers executed: {len(result['investigation_results'])}")
    print("=" * 55)
    print()
    print("📋 TROUBLESHOOTING REPORT")
    print("-" * 55)
    print(result["final_report"])
