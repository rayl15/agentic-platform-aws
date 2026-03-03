from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import uuid4
from agentic_platform.core.models.streaming_models import StreamEvent
from agentic_platform.core.models.vectordb_models import VectorSearchRequest, VectorSearchResponse
from agentic_platform.core.models.memory_models import (
    ToolCall, 
    Content, 
    TextContent, 
    ImageContent, 
    AudioContent, 
    JsonContent,
    ToolResult, 
    Message, 
    SessionContext
)

##############################################################################
# Agentic API Types
##############################################################################

class AgenticRequest(BaseModel):
    """Request to invoke an agent"""
    message: Message
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    stream: bool = False
    
    # Simple configuration
    max_tokens: Optional[int] = None
    include_thinking: bool = False
    
    # Context and metadata
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Convenience constructor for simple text requests
    @classmethod
    def from_text(cls, text: str, **kwargs) -> "AgenticRequest":
        """Create request from simple text"""
        user_message = Message.from_text("user", text)
        return cls(message=user_message, **kwargs)
    
    # Convenience property to get the last user message text
    @property
    def user_text(self) -> Optional[str]:
        """Get the text from the most recent user message"""
        if self.message.role == "user" and self.message.text:
            return self.message.text
        return None
    
    # Alias for compatibility with workflow controllers
    @property
    def latest_user_text(self) -> Optional[str]:
        """Get the text from the most recent user message (alias for user_text)"""
        return self.user_text

class AgenticRequestStream(AgenticRequest):
    """Request model for streaming agent tasks"""
    stream: bool = True

class AgenticResponse(BaseModel):
    """Response from agent invocation"""
    message: Message  # The assistant's response message
    session_id: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Convenience properties
    @property
    def text(self) -> Optional[str]:
        """Get the response text"""
        return self.message.text
    
    @property
    def json_data(self) -> List[Dict[str, Any]]:
        """Get all JSON content from the response"""
        if not self.message.content:
            return []
        return [
            item.content for item in self.message.content 
            if item.type == "json"
        ]
    
    @property
    def tool_calls(self) -> List[ToolCall]:
        """Get all tool calls from the response"""
        return self.message.tool_calls
    
    @property
    def has_errors(self) -> bool:
        """Check if any tool results contain errors"""
        return any(result.isError for result in self.message.tool_results)

##############################################################################
# Memory/Retrieval Models (Gateway Services)
##############################################################################

class RetrieveRequest(BaseModel):
    """Request model for retrieve using vector search."""
    vectorsearch_request: VectorSearchRequest

class RetrieveResponse(BaseModel):
    """Response model for retrieve"""
    vectorsearch_results: VectorSearchResponse
