# Continue with regular imports.
from fastapi import FastAPI
from agentic_platform.core.middleware.configure_middleware import configuration_server_middleware
from agentic_platform.core.models.api_models import RetrieveRequest, RetrieveResponse
from agentic_platform.service.retrieval_gateway.api.retrieve_controller import RetrieveController

app = FastAPI()

# Configure middelware that's common to all servers.
configuration_server_middleware(app, path_prefix="/api/retrieval-gateway")

@app.post("/retrieve")
async def retrieve(request: RetrieveRequest) -> RetrieveResponse:
    """Retrieve using vector search."""
    return RetrieveController.retrieve(request)


@app.get("/health")
async def health():
    """
    Health check endpoint for Kubernetes probes.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) # nosec B104 - Binding to all interfaces within container is intended