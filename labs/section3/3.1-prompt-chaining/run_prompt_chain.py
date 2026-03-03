#!/usr/bin/env python3
"""Run the Prompt Chaining workflow - Documentation Explainer."""

import sys
import chromadb
import boto3
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Type, TypedDict
from langgraph.graph import StateGraph, START, END

# ─── Setup ───────────────────────────────────────────────────────────────────

chroma_client = chromadb.PersistentClient(path="../../data/chroma")
session = boto3.Session()
bedrock = session.client(service_name="bedrock-runtime")

EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
HAIKU_MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

embedding_function = AmazonBedrockEmbeddingFunction(session=session, model_name=EMBEDDING_MODEL_ID)
collection = chroma_client.get_collection(name="opensearch-docs-rag", embedding_function=embedding_function)

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

SYSTEM_PROMPT = "You are a helpful assistant that explains OpenSearch documentation in simple terms."

class ExtractConceptPrompt(BasePrompt):
    system_prompt: str = SYSTEM_PROMPT
    user_prompt: str = """Extract key concepts from this documentation:
<query>{question}</query>
<documentation>{context}</documentation>
Format as a bulleted list of core concepts."""

class SimplifyExplanationPrompt(BasePrompt):
    system_prompt: str = SYSTEM_PROMPT
    user_prompt: str = """Explain these concepts simply:
{concepts}
Write for someone new to OpenSearch. Use analogies."""

class GenerateExamplesPrompt(BasePrompt):
    system_prompt: str = SYSTEM_PROMPT
    user_prompt: str = """Create practical examples for:
Concepts: {concepts}
Explanation: {explanation}
Include code snippets and common pitfalls."""

class FormatOutputPrompt(BasePrompt):
    system_prompt: str = SYSTEM_PROMPT
    user_prompt: str = """# Documentation Breakdown
## Key Concepts
{concepts}
## Simple Explanation
{explanation}
## Examples
{examples}"""

# ─── Helper Functions ────────────────────────────────────────────────────────

def call_bedrock(prompt: BasePrompt) -> str:
    response = bedrock.converse(
        modelId=prompt.model_id,
        inferenceConfig=prompt.hyperparams,
        messages=[{"role": "user", "content": [{"text": prompt.user_prompt}]}],
        system=[{"text": prompt.system_prompt}],
    )
    return response["output"]["message"]["content"][0]["text"]

def do_rag(query: str, prompt_class: Type[BasePrompt]) -> str:
    results = collection.query(query_texts=[query], n_results=2)
    context = "\n\n".join(results["documents"][0])
    prompt = prompt_class(inputs={"question": query, "context": context})
    return call_bedrock(prompt)

# ─── State & Nodes ───────────────────────────────────────────────────────────

class ExplainerState(TypedDict):
    query: str
    concepts: str
    explanation: str
    examples: str
    final_output: str

def extract_concepts(state: ExplainerState) -> ExplainerState:
    print("Step 1: Extracting concepts... (RAG + LLM)")
    state["concepts"] = do_rag(state["query"], ExtractConceptPrompt)
    print("        ✓ Concepts extracted")
    return state

def simplify_explanation(state: ExplainerState) -> ExplainerState:
    print("Step 2: Simplifying explanation... (LLM)")
    prompt = SimplifyExplanationPrompt(inputs={"concepts": state["concepts"]})
    state["explanation"] = call_bedrock(prompt)
    print("        ✓ Explanation simplified")
    return state

def generate_examples(state: ExplainerState) -> ExplainerState:
    print("Step 3: Generating examples... (LLM)")
    prompt = GenerateExamplesPrompt(inputs={"concepts": state["concepts"], "explanation": state["explanation"]})
    state["examples"] = call_bedrock(prompt)
    print("        ✓ Examples generated")
    return state

def format_output(state: ExplainerState) -> ExplainerState:
    print("Step 4: Formatting output... (LLM)")
    prompt = FormatOutputPrompt(inputs={"concepts": state["concepts"], "explanation": state["explanation"], "examples": state["examples"]})
    state["final_output"] = call_bedrock(prompt)
    print("        ✓ Output formatted")
    return state

# ─── Build Graph ─────────────────────────────────────────────────────────────

def create_workflow() -> StateGraph:
    workflow = StateGraph(ExplainerState)
    workflow.add_node("extract_concepts", extract_concepts)
    workflow.add_node("simplify_explanation", simplify_explanation)
    workflow.add_node("generate_examples", generate_examples)
    workflow.add_node("format_output", format_output)
    
    workflow.add_edge(START, "extract_concepts")
    workflow.add_edge("extract_concepts", "simplify_explanation")
    workflow.add_edge("simplify_explanation", "generate_examples")
    workflow.add_edge("generate_examples", "format_output")
    workflow.add_edge("format_output", END)
    
    return workflow.compile()

# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Explain OpenSearch security configuration"
    
    print()
    print("🔗 Prompt Chaining: Documentation Explainer")
    print("=" * 50)
    print(f"Query: {query}")
    print("=" * 50)
    print()
    
    graph = create_workflow()
    state = ExplainerState(query=query, concepts="", explanation="", examples="", final_output="")
    result = graph.invoke(state)
    
    print()
    print("=" * 50)
    print("📚 RESULT")
    print("=" * 50)
    print(result["final_output"])
