from pydantic import BaseModel, Field

from agentic_platform.tool.retrieval.retrieval_tool_prompt import RAGPrompt
from agentic_platform.core.models.llm_models import LLMRequest, LLMResponse
from agentic_platform.core.models.memory_models import Message
from agentic_platform.core.client.retrieval_gateway.retrieval_gateway_client import RetrievalGatewayClient
from agentic_platform.core.models.vectordb_models import VectorSearchRequest, VectorSearchResponse
from agentic_platform.core.client.llm_gateway.llm_gateway_client import LLMGatewayClient
class RAGInput(BaseModel):
    """Input model for knowledge base queries"""
    query_text: str = Field(description="The search query to find relevant information")


def retrieve_and_answer(input_data: RAGInput) -> str:
    """Search the knowledge base for relevant information based on a query."""
    # Perform the search
    response: VectorSearchResponse = RetrievalGatewayClient.retrieve(VectorSearchRequest(query=input_data.query_text))
    # Aggregate the results into a single string
    context: str = "\n".join([result.text for result in response.results])
    # Create the RAG prompt
    rag_prompt: RAGPrompt = RAGPrompt(inputs={"user_message": input_data.query_text, "context": context})
    # Build out the LLMRequest.
    llm_request: LLMRequest = LLMRequest(
        system_prompt=rag_prompt.system_prompt,
        messages=[Message(role="user", text=rag_prompt.user_prompt)],
        model_id=rag_prompt.model_id,
        hyperparams=rag_prompt.hyperparams
    )
    # Call Bedrock through the client.
    rag_response: LLMResponse = LLMGatewayClient.chat_invoke(llm_request)    
    
    return rag_response.text