from agentic_platform.core.models.memory_models import (
    CreateMemoryRequest,
    CreateMemoryResponse
)
from agentic_platform.service.memory_gateway.client.memory.memory_client import MemoryClient

class CreateMemoryController:
    @staticmethod
    def create_memory(request: CreateMemoryRequest) -> CreateMemoryResponse:
        return MemoryClient.create_memory(request)