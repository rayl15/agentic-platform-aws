# src/agentic_platform/core/middleware/auth/auth_middleware.py
from typing import Callable, List, TypeVar, Awaitable, Optional, Dict, Any, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp
import logging  
from agentic_platform.core.models.auth_models import AgenticPlatformAuth
from agentic_platform.core.middleware.auth.token_verifier import CognitoTokenVerifier, TokenVerifier
from agentic_platform.core.middleware.auth.token_auth_converter import TokenAuthConverter, CognitoTokenAuthConverter
import os

T = TypeVar('T', bound=ASGIApp)

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware supporting both user and M2M authentication"""
    
    def __init__(self, app: T, excluded_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or ["/health", "/docs", "/openapi.json"]
        self.token_verifier: TokenVerifier = CognitoTokenVerifier()
        self.token_auth_converter: TokenAuthConverter = CognitoTokenAuthConverter()
    
    def is_path_excluded(self, path: str) -> bool:
        """Check if a path is excluded from authentication."""
        for excluded_path in self.excluded_paths:
            if path == excluded_path or path.startswith(excluded_path):
                return True
        return False
    
    def check_auth_configuration(self) -> None:
        """Verify that authentication is properly configured."""
        if not self.token_verifier:
            logger.error("Authentication not properly configured")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication system unavailable"
            )
    
    def extract_token_from_header(self, request: Request) -> str:
        """Extract the Bearer token from the Authorization header."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header:
            logger.warning("Missing Authorization header")
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Authentication required")
        
        token_parts = auth_header.split()
        if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
            logger.warning("Invalid Authorization header format")
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format")
        
        return token_parts[1]
    
    def authenticate_request(self, request: Request) -> AgenticPlatformAuth:
        """
        Authenticate the request using available auth methods.
        This can be overridden in subclasses to add additional auth methods.
        """
        # Extract token from header
        token = self.extract_token_from_header(request)
        # Validate token using public key cert and get payload
        token_payload = self.token_verifier.validate_token(token)
        # Convert token payload to AgenticPlatformAuth type
        auth_result: AgenticPlatformAuth = self.token_auth_converter.convert_token(token_payload, request.headers)
        # Return the auth result
        return auth_result
    
    def store_auth_result(self, request: Request, auth_result: AgenticPlatformAuth) -> None:
        """Store authentication result in request state."""
        # Store the auth result in request state
        request.state.auth = auth_result
        
        # For backwards compatibility - store user info in the old format too
        if auth_result.type == "user" and auth_result.user:
            request.state.user = {
                'user_id': auth_result.user.user_id,
                'attributes': auth_result.user.metadata
            }
        elif auth_result.type == "service" and auth_result.service:
            request.state.service = {
                'service_id': auth_result.service.service_id,
                'attributes': auth_result.service.metadata
            }
            
        return
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Process the request through authentication middleware.
        This method orchestrates the authentication flow.
        """
        # Skip authentication for excluded paths
        path = request.scope["path"]
        if self.is_path_excluded(path):
            return await call_next(request)
        
        # Skip authentication for OPTIONS requests (CORS preflight)
        method = request.scope["method"]
        if method == "OPTIONS":
            return await call_next(request)
        
        # Skip authentication entirely for local environment (integration testing)
        environment = os.getenv("ENVIRONMENT", "").lower()
        if environment == "local":
            logger.info("Skipping authentication for local environment")
            # Create a mock auth result for local testing
            from agentic_platform.core.models.auth_models import AgenticPlatformAuth, UserAuth
            mock_auth = AgenticPlatformAuth(
                type="user",
                user=UserAuth(
                    user_id="test-user-123",
                    username="test-user",
                    email="test@example.com",
                    provider="local",
                    metadata={"test": True}
                )
            )
            self.store_auth_result(request, mock_auth)
            return await call_next(request)
        
        # Check that auth is properly configured
        self.check_auth_configuration()
        
        # Authenticate the request
        auth_result: AgenticPlatformAuth = self.authenticate_request(request)
        
        # Store the result in request state
        self.store_auth_result(request, auth_result)
            
        # Continue with the request - authentication successful
        return await call_next(request)
