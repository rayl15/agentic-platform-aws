import os
import requests
from agentic_platform.core.models.vectordb_models import VectorSearchRequest, VectorSearchResponse
from agentic_platform.core.context.request_context import get_auth_token
RETRIEVAL_GATEWAY_URL = os.getenv("RETRIEVAL_GATEWAY_ENDPOINT")
DEFAULT_TIMEOUT = 7  # Default timeout in seconds

class RetrievalGatewayClient:
    """
    Shim for calling a vectorDB through a microservice. 
    Makes it easy to swap out vectorDBs, add graph RAG, etc..
    """

    @classmethod
    def _get_auth_headers(cls):
        """Helper method to get authentication headers consistently"""
        auth_token = get_auth_token()
        if auth_token:
            return {'Authorization': f'Bearer {auth_token}'}
        return {}  # Return empty dict if no token
    
    @classmethod
    def retrieve(cls, request: VectorSearchRequest) -> VectorSearchResponse:
        headers = cls._get_auth_headers()
        response = requests.post(
            f"{RETRIEVAL_GATEWAY_URL}/retrieve", 
            json=request.model_dump(),
            timeout=DEFAULT_TIMEOUT,
            headers=headers
        )
        response.raise_for_status()
        return VectorSearchResponse(**response.json())
