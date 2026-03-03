from typing import Optional, List
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from starlette.types import ASGIApp
import logging

from agentic_platform.core.observability.provider.base_observability_provider import BaseObservabilityProvider
from agentic_platform.core.observability.provider.otel_provider import OpenTelemetryProvider
from agentic_platform.core.observability.observability_facade import configure_facade

logger = logging.getLogger(__name__)

class TelemetryMiddleware(BaseHTTPMiddleware):
    """
    Middleware that sets up OpenTelemetry instrumentation.
    Configures the telemetry facade and enables auto-instrumentation.
    """
    
    def __init__(
        self, 
        app: ASGIApp, 
        service_name: str = "fastapi-app",
        service_version: str = "0.1.0",
        excluded_paths: List[str] = None,
    ):
        super().__init__(app)
        self.excluded_paths = excluded_paths or ["/health", "/metrics"]

        
        # Set up telemetry provider
        try:
            provider: BaseObservabilityProvider = OpenTelemetryProvider(
                service_name=service_name,
                service_version=service_version
            )
            
            # Configure the global telemetry facade
            self.telemetry = configure_facade(service_name, provider)
            self.telemetry.info(f"Telemetry configured for {service_name} v{service_version}")

            # BedrockInstrumentor().instrument()
            
        except Exception as e:
            logger.error(f"Error initializing telemetry: {e}")
            self.telemetry = None
    
    async def dispatch(self, request: Request, call_next):
        # Skip telemetry for excluded paths
        path = request.scope["path"]
        for excluded_path in self.excluded_paths:
            if path == excluded_path or path.startswith(excluded_path):
                return await call_next(request)
        
        # Handle the request - auto-instrumentation creates spans automatically
        response = await call_next(request)
        return response