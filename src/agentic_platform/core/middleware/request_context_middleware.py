# src/agentic_platform/core/middleware/context_middleware.py
from typing import Callable, TypeVar, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from starlette.types import ASGIApp
import logging

from agentic_platform.core.context.request_context import set_auth_token, set_auth_context
from agentic_platform.core.models.auth_models import AgenticPlatformAuth

T = TypeVar('T', bound=ASGIApp)

logger = logging.getLogger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that stores authentication information in context variables.
    
    This middleware should be placed after AuthMiddleware to access the
    authentication results stored in request.state.
    
    It provides a clean way to access authentication data from any part of the 
    application without passing it explicitly through function calls.
    """
    
    def __init__(self, app: T):
        super().__init__(app)
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Store authentication information in context variables if available.
        """
        # Check if we have auth information from a previous middleware
        if hasattr(request.state, 'auth'):
            # Get the auth info from request state
            auth: AgenticPlatformAuth = request.state.auth
            
            # Store in context variable for access from anywhere
            set_auth_context(auth)
            
            # If there's a token in the headers, store that too
            auth_header = request.headers.get("Authorization", "")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                set_auth_token(token)
                logger.debug("Auth token stored in context")
        
        # Continue with the request
        response: Response = await call_next(request)
        return response