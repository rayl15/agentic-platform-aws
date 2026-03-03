from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field

# Service auth result - provider agnostic
class ServiceAuth(BaseModel):
    """Authentication details for service accounts, not tied to any specific platform"""
    service_id: str  # Unique service identifier
    name: str  # Service name
    namespace: Optional[str] = None  # Optional namespace/environment/context
    groups: List[str] = Field(default_factory=list)  # Service groups/roles
    provider: str = "generic"  # Which auth provider (kubernetes, istio, etc)
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Provider-specific attributes

# Generic User auth result - not tied to any provider
class UserAuth(BaseModel):
    """Authentication details for users, not tied to any specific platform"""
    user_id: str  # Unique identifier
    username: Optional[str] = None  # Human-readable username
    email: Optional[str] = None  # Email address if available
    groups: List[str] = Field(default_factory=list)  # User groups/roles
    provider: str = "generic"  # Which auth provider (cognito, okta, etc)
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Provider-specific attributes

# The main auth result as a tagged union
class AgenticPlatformAuth(BaseModel):
    """Authentication result with discriminated union pattern"""
    type: Literal["service", "user", "api_key"]
    service: Optional[ServiceAuth] = None
    user: Optional[UserAuth] = None
        
    # Factory methods for cleaner creation
    @classmethod
    def from_service(cls, service: ServiceAuth) -> "AgenticPlatformAuth":
        return cls(type="service", service=service)
        
    @classmethod
    def from_user(cls, user: UserAuth) -> "AgenticPlatformAuth":
        return cls(type="user", user=user)
