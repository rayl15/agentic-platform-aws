from agentic_platform.core.models.memory_models import (
    UpsertSessionContextRequest,
    UpsertSessionContextResponse
)
from agentic_platform.service.memory_gateway.client.memory.memory_client import MemoryClient

class UpsertSessionContextController:
    @staticmethod
    def upsert_session_context(request: UpsertSessionContextRequest) -> UpsertSessionContextResponse:
        return MemoryClient.upsert_session_context(request)