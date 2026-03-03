#!/usr/bin/env python3
"""Run the Intelligent Routing workflow - Question Classifier."""

import sys
import chromadb
import boto3
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Type, TypedDict
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

CLASSIFY_SYSTEM = "You are a helpful assistant specializing in OpenSearch documentation and support."

RAG_SYSTEM = """You are a helpful assistant specializing in OpenSearch documentation and support.
<instructions>
1. Answer the question using only the documentation provided
2. Be clear and concise with your answer
3. Avoid saying "based on the context provided"
4. If the answer isn't in the documentation, say "I don't know"
</instructions>"""

class ClassifyPrompt(BasePrompt):
    system_prompt: str = CLASSIFY_SYSTEM
    user_prompt: str = """Classify this OpenSearch question into exactly one category:

Question: {question}

Categories:
- INSTALL: Installation, setup, cluster configuration
- SECURITY: Security, authentication, access control
- QUERY: Querying, indexing, search operations
- PERFORMANCE: Optimization, scaling, monitoring

Respond with only the category code (e.g., 'INSTALL')."""

class InstallationPrompt(BasePrompt):
    system_prompt: str = RAG_SYSTEM
    user_prompt: str = """Using the question and context below, provide installation guidance:

<question>{question}</question>
<context>{context}</context>

Include:
- Step-by-step instructions
- System requirements
- Configuration options
- Common issues and solutions"""

class SecurityPrompt(BasePrompt):
    system_prompt: str = RAG_SYSTEM
    user_prompt: str = """Using the question and context below, provide security guidance:

<question>{question}</question>
<context>{context}</context>

Include:
- Security best practices
- Authentication setup
- Access control configuration
- Security implications"""

class QueryPrompt(BasePrompt):
    system_prompt: str = RAG_SYSTEM
    user_prompt: str = """Using the question and context below, provide querying guidance:

<question>{question}</question>
<context>{context}</context>

Include:
- Query examples
- Index configuration
- Best practices
- Performance considerations"""

class PerformancePrompt(BasePrompt):
    system_prompt: str = RAG_SYSTEM
    user_prompt: str = """Using the question and context below, provide performance guidance:

<question>{question}</question>
<context>{context}</context>

Include:
- Optimization strategies
- Scaling considerations
- Monitoring tips
- Resource management"""

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

class WorkflowState(TypedDict):
    question: str
    category: str
    response: str

def classify_question(state: WorkflowState) -> Dict[str, str]:
    """Classify the question into a category."""
    prompt = ClassifyPrompt(inputs={"question": state["question"]})
    category = call_bedrock(prompt).strip()
    return {"category": category}

def handle_installation(state: WorkflowState) -> WorkflowState:
    """Handle installation & setup questions."""
    state["response"] = do_rag(state["question"], InstallationPrompt)
    return state

def handle_security(state: WorkflowState) -> WorkflowState:
    """Handle security & authentication questions."""
    state["response"] = do_rag(state["question"], SecurityPrompt)
    return state

def handle_querying(state: WorkflowState) -> WorkflowState:
    """Handle querying & indexing questions."""
    state["response"] = do_rag(state["question"], QueryPrompt)
    return state

def handle_performance(state: WorkflowState) -> WorkflowState:
    """Handle performance optimization questions."""
    state["response"] = do_rag(state["question"], PerformancePrompt)
    return state

# ─── Build Graph ─────────────────────────────────────────────────────────────

def create_routing_workflow() -> StateGraph:
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("classify", classify_question)
    workflow.add_node("install", handle_installation)
    workflow.add_node("security", handle_security)
    workflow.add_node("query", handle_querying)
    workflow.add_node("performance", handle_performance)

    # Entry point
    workflow.add_edge(START, "classify")

    # Conditional routing based on classification
    workflow.add_conditional_edges(
        "classify",
        lambda state: state["category"],
        {
            "INSTALL": "install",
            "SECURITY": "security",
            "QUERY": "query",
            "PERFORMANCE": "performance",
        }
    )

    # All handlers lead to END
    workflow.add_edge("install", END)
    workflow.add_edge("security", END)
    workflow.add_edge("query", END)
    workflow.add_edge("performance", END)

    return workflow.compile()

# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "How do I install OpenSearch on AWS?"

    print()
    print("🔀 Intelligent Routing: Question Classifier")
    print("=" * 50)
    print(f"Question: {question}")
    print("=" * 50)
    print()

    graph = create_routing_workflow()
    state = WorkflowState(question=question, category="", response="")
    result = graph.invoke(state)

    print(f"📊 Category: {result['category']}")
    print()
    print("=" * 50)
    print("💬 RESPONSE")
    print("=" * 50)
    print(result["response"])
