from agentic_platform.core.models.vectordb_models import VectorSearchRequest, VectorSearchResponse
from agentic_platform.service.retrieval_gateway.client.kb_client import BedrockKnowledgeBaseClient

class VectorSearchClient:
    """Shim for calling a vectorDB. Makes it easy to swap out vectorDBs."""
    @classmethod
    def retrieve(cls, request: VectorSearchRequest) -> VectorSearchResponse:
        return BedrockKnowledgeBaseClient.retrieve(request)
