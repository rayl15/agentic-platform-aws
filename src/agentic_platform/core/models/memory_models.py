from typing import Dict, Any, Optional, List, Literal, Union, Annotated
from pydantic import BaseModel, Field, field_validator, Discriminator
from uuid import uuid4
from datetime import datetime

##############################################################################
# Define a ToolCall type. This follows the MCP Tool specs params.
# Doing this allows us to easily extend ToolCall objects to fully support MCP.
# with a simple decorator to add method, jsonrpc, and id.
##############################################################################

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]
    id: Optional[str] = None

##########################################################################
# MCP is standardizing the way we return results however it's incomplete. 
# Bedrock for example has video and json results as well.
# However bedrock has text, json, document, image, and video. 
# We'll intentionally leave it open ended for now until MCP is updated.
##########################################################################

class BaseContent(BaseModel):
    type: Literal["text", "image", "audio", "json"]

class TextContent(BaseContent):
    type: Literal["text"] = "text"
    text: str

class ImageContent(BaseContent):
    type: Literal["image"] = "image"
    data: str  # base64-encoded data
    mimeType: str  # e.g., "image/png"

class AudioContent(BaseContent):
    type: Literal["audio"] = "audio"
    data: str  # base64-encoded audio data
    mimeType: str  # e.g., "audio/wav"

# This is not a part of MCP, but it's supported by Bedrock making ours a superset of MCP.
class JsonContent(BaseContent):
    type: Literal["json"] = "json"
    content: Dict[str, Any]

# Create a discriminated union for proper serialization/deserialization
Content = Annotated[
    Union[TextContent, ImageContent, AudioContent, JsonContent],
    Discriminator('type')
]

# With this approach we're able to support a superset of MCP and Bedrock message types.
class ToolResult(BaseModel):
    """A tool result"""
    # ToolUse Id is optional and can be added post instantiation by the calling agent.
    id: Optional[str] = None
    content: List[Content]
    isError: bool = False

    @classmethod
    def to_content(cls, value: Any) -> List[Content]:
        """Convert any Python value to properly typed content items"""
        # Handle None
        if value is None:
            return []
            
        # Already a content item
        if isinstance(value, (TextContent, ImageContent, AudioContent, JsonContent)):
            return [value]
            
        # String -> TextContent
        if isinstance(value, str):
            return [TextContent(type="text", text=value)]
            
        # Dict -> JsonContent
        if isinstance(value, dict):
            return [JsonContent(type="json", content=value)]
            
        # List -> Process each item and flatten
        if isinstance(value, (list, tuple)):
            result = []
            for item in value:
                result.extend(cls.to_content(item))
            return result
            
        # Other types -> Try JSON, fall back to string
        try:
            # If it's a simple type like int, float, bool
            if isinstance(value, (int, float, bool)):
                return [TextContent(type="text", text=str(value))]
                
            # For other objects, try JSON
            import json
            return [JsonContent(type="json", content=value)]
        except:
            return [TextContent(type="text", text=str(value))]

class MediaInfo(BaseModel):
    """Container for media data and metadata"""
    data: str
    mime_type: str = "application/octet-stream"

class Message(BaseModel):
    """A message in the conversation"""
    role: Literal["user", "assistant"]
    content: Optional[List[Content]] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)
    tool_results: List[ToolResult] = Field(default_factory=list)
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    
    def __init__(self, role: str, text: Optional[str] = None, **data):
        """Initialize a Message with optional text parameter for convenience."""
        if text is not None and 'content' not in data:
            # If text is provided but content isn't, create content with text
            data['content'] = [TextContent(type="text", text=text)]
        super().__init__(role=role, **data)

    @property
    def timestamp_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp)

    def _get_content_by_type(self, content_type: str):
        if self.content:
            for item in self.content:
                if getattr(item, 'type', None) == content_type:
                    return item
        return None

    def get_text_content(self) -> Optional[TextContent]:
        return self._get_content_by_type("text")

    def get_image_content(self) -> Optional[ImageContent]:
        return self._get_content_by_type("image")

    def get_audio_content(self) -> Optional[AudioContent]:
        return self._get_content_by_type("audio")

    def get_json_content(self) -> Optional[JsonContent]:
        return self._get_content_by_type("json")

    @property
    def text(self) -> Optional[str]:
        # Convenience property: returns the aggregate of all text content blocks as a single string, or None if there are none.
        if not self.content:
            return None
        
        texts = [item.text for item in self.content if getattr(item, 'type', None) == "text"]
        return " ".join(texts) if texts else None

    @classmethod
    def from_text(cls, role: str, text: str, **kwargs) -> "Message":
        """Convenience constructor to create a Message with a single TextContent block."""
        return cls(role=role, content=[TextContent(type="text", text=text)], **kwargs)

class SessionContext(BaseModel):
    """Represents a single conversation"""
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    messages: List[Message] = Field(default_factory=list)
    system_prompt: Optional[str] = None
    # You can pass graph checkpoints here.
    session_metadata: Optional[Dict[str, Any]] = None
    
    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def add_messages(self, messages: List[Message]) -> None:
        self.messages.extend(messages)

    def get_messages(self) -> List[Message]:
        """Get messages"""
        return self.messages
    
    def add_metadata(self, metadata: Dict[str, Any]) -> None:
        self.session_metadata = metadata

class Memory(BaseModel):
    memory_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    user_id: str
    agent_id: str
    content: str
    embedding_model: str
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    embedding: Optional[List[float]] = None
    similarity: float = -1.0
    

class GetSessionContextRequest(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class GetSessionContextResponse(BaseModel):
    results: List[SessionContext]

class UpsertSessionContextRequest(BaseModel):
    session_context: SessionContext
    
class UpsertSessionContextResponse(BaseModel):
    session_context: SessionContext
    
class GetMemoriesRequest(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    embedding: Optional[List[float]] = None
    limit: int = 2

    # Add validation so you can't get memories of an agent without session or user
    @field_validator("agent_id")
    @classmethod
    def validate_agent_id(cls, v, info):
        data = info.data
        if not data.get("session_id") and not data.get("user_id"):
            raise ValueError("Either session_id or user_id must be provided")
        return v

class GetMemoriesResponse(BaseModel):
    memories: List[Memory]
    
class CreateMemoryRequest(BaseModel):
    session_id: str
    user_id: str
    agent_id: str
    session_context: SessionContext
    
class CreateMemoryResponse(BaseModel):
    memory: Memory
