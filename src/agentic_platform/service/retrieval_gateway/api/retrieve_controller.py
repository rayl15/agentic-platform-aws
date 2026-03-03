from agentic_platform.core.models.api_models import RetrieveRequest, RetrieveResponse
from agentic_platform.core.models.vectordb_models import VectorSearchResponse
from agentic_platform.service.retrieval_gateway.client.vectorsearch_client import VectorSearchClient

class RetrieveController:

    @classmethod
    def retrieve(cls, request: RetrieveRequest) -> RetrieveResponse:
        response: VectorSearchResponse = VectorSearchClient.retrieve(request.vectorsearch_request)
        print(f"Response: {response}")
        return RetrieveResponse(vectorsearch_results=response)