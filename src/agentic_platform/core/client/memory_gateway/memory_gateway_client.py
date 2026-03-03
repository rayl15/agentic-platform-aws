import os
import requests
from agentic_platform.core.models.memory_models import (
    GetSessionContextRequest,
    GetSessionContextResponse,
    UpsertSessionContextRequest,
    UpsertSessionContextResponse,
    GetMemoriesRequest,
    GetMemoriesResponse,
    CreateMemoryRequest,
    CreateMemoryResponse
)
from agentic_platform.core.context.request_context import get_auth_token
MEMORY_GATEWAY_URL = os.getenv("MEMORY_GATEWAY_ENDPOINT")
DEFAULT_TIMEOUT = 7  # Default timeout in seconds

class MemoryGatewayClient:
    """
    Shim for calling a memory gateway through a microservice. 
    Makes it easy to swap out memory gateways, add graph RAG, etc..
    """
    
    @classmethod
    def _get_auth_headers(cls):
        """Helper method to get authentication headers consistently"""
        auth_token = get_auth_token()
        if auth_token:
            return {'Authorization': f'Bearer {auth_token}'}
        return {}  # Return empty dict if no token
    
    @classmethod
    def get_session_context(cls, request: GetSessionContextRequest) -> GetSessionContextResponse:
        headers = cls._get_auth_headers()
        response = requests.post(
            f"{MEMORY_GATEWAY_URL}/get-session-context", 
            json=request.model_dump(),
            timeout=DEFAULT_TIMEOUT,
            headers=headers
        )
        response.raise_for_status()
        return GetSessionContextResponse(**response.json())
    
    @classmethod
    def upsert_session_context(cls, request: UpsertSessionContextRequest) -> UpsertSessionContextResponse:
        headers = cls._get_auth_headers()
        response = requests.post(
            f"{MEMORY_GATEWAY_URL}/upsert-session-context", 
            json=request.model_dump(),
            timeout=DEFAULT_TIMEOUT,
            headers=headers
        )
        response.raise_for_status()
        return UpsertSessionContextResponse(**response.json())
    
    @classmethod
    def get_memories(cls, request: GetMemoriesRequest) -> GetMemoriesResponse:
        headers = cls._get_auth_headers()
        response = requests.post(
            f"{MEMORY_GATEWAY_URL}/get-memories", 
            json=request.model_dump(),
            timeout=DEFAULT_TIMEOUT,
            headers=headers
        )
        response.raise_for_status()
        return GetMemoriesResponse(**response.json())
    
    @classmethod
    def create_memory(cls, request: CreateMemoryRequest) -> CreateMemoryResponse:
        headers = cls._get_auth_headers()
        response = requests.post(
            f"{MEMORY_GATEWAY_URL}/create-memory", 
            json=request.model_dump(),
            timeout=DEFAULT_TIMEOUT,
            headers=headers
        )
        response.raise_for_status()
        return CreateMemoryResponse(**response.json())