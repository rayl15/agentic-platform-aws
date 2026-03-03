# Continue with regular imports.
from fastapi import FastAPI
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
from agentic_platform.core.middleware.configure_middleware import configuration_server_middleware
from agentic_platform.service.memory_gateway.api.get_session_controller import GetSessionContextController
from agentic_platform.service.memory_gateway.api.upsert_session_controller import UpsertSessionContextController
from agentic_platform.service.memory_gateway.api.get_memory_controller import GetMemoriesController
from agentic_platform.service.memory_gateway.api.create_memory_controller import CreateMemoryController

app = FastAPI()

# Configure middelware that's common to all servers.
configuration_server_middleware(app, path_prefix="/api/memory-gateway")

@app.post("/get-session-context")
async def get_session_context(request: GetSessionContextRequest) -> GetSessionContextResponse:
    """Get the session context for a given session id."""
    return GetSessionContextController.get_session_context(request)

@app.post("/upsert-session-context")
async def upsert_session_context(request: UpsertSessionContextRequest) -> UpsertSessionContextResponse:
    """Upsert the session context for a given session id."""
    return UpsertSessionContextController.upsert_session_context(request)

@app.post("/get-memories")
async def get_memories(request: GetMemoriesRequest) -> GetMemoriesResponse:
    """Get the memories for a given session id."""
    return GetMemoriesController.get_memories(request)

@app.post("/create-memory")
async def create_memory(request: CreateMemoryRequest) -> CreateMemoryResponse:
    """Create a memory for a given session id."""
    return CreateMemoryController.create_memory(request)

@app.get("/health")
async def health():
    """
    Health check endpoint for Kubernetes probes.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)  # nosec B104 - Binding to all interfaces within container is intended