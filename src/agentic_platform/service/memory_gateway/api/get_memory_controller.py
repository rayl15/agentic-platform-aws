from agentic_platform.core.models.memory_models import (
    GetMemoriesRequest,
    GetMemoriesResponse
)
from agentic_platform.service.memory_gateway.client.memory.memory_client import MemoryClient

class GetMemoriesController:
    @staticmethod
    def get_memories(request: GetMemoriesRequest) -> GetMemoriesResponse:
        return MemoryClient.get_memories(request)
