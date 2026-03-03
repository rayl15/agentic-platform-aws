# src/agentic_platform/core/context/request_context.py
import contextvars
from typing import Optional

from agentic_platform.core.models.auth_models import AgenticPlatformAuth

# Context variables to store request-specific data
auth_token_var = contextvars.ContextVar('auth_token', default=None)
auth_context_var = contextvars.ContextVar('auth_context', default=None)

def set_auth_token(token: str) -> None:
    """Set the current request's auth token"""
    auth_token_var.set(token)

def get_auth_token() -> Optional[str]:
    """Get the current request's auth token"""
    return auth_token_var.get()

def set_auth_context(context: AgenticPlatformAuth) -> None:
    """Set the current request's auth context"""
    auth_context_var.set(context)

def get_auth_context() -> Optional[AgenticPlatformAuth]:
    """Get the current request's auth context"""
    return auth_context_var.get()