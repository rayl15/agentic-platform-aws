from agentic_platform.core.models.memory_models import (
    GetSessionContextRequest,
    GetSessionContextResponse
)
from agentic_platform.service.memory_gateway.client.memory.memory_client import MemoryClient

class GetSessionContextController:
    @staticmethod
    def get_session_context(request: GetSessionContextRequest) -> GetSessionContextResponse:
        return MemoryClient.get_session_context(request)