from pydantic import BaseModel, Field, Discriminator
from typing import Optional, Dict, Any, List, Literal, Union, Annotated
from enum import Enum
from uuid import uuid4
from datetime import datetime
from agentic_platform.core.models.memory_models import (
    BaseContent, TextContent, ImageContent, AudioContent, JsonContent,
    ToolCall, ToolResult, Message
)
from agentic_platform.core.models.prompt_models import BasePrompt
import json
from fastapi import Response, status

class StreamEventType(str, Enum):
    """Types of events that can be streamed"""
    START = "start"                             # Stream started
    CONTENT_BLOCK_START = "content_block_start" # Start of a content block
    CONTENT_BLOCK_END = "content_block_end"     # End of a content block
    TEXT_DELTA = "text_delta"                   # A chunk of text content
    THINKING_DELTA = "thinking_delta"           # Agent's internal reasoning
    TOOL_CALL = "tool_call"                     # Tool being called
    TOOL_CALL_DELTA = "tool_call_delta"         # Tool call delta"
    TOOL_RESULT = "tool_result"                 # Result from tool
    ERROR = "error"                             # Error occurred
    DONE = "done"                               # Stream complete

class BaseStreamEvent(BaseModel):
    """Base class for stream events"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StartEvent(BaseStreamEvent):
    """Event signaling text content is complete"""
    type: Literal[StreamEventType.START] = StreamEventType.START
class TextDeltaEvent(BaseStreamEvent):
    """Event containing a chunk of text"""
    type: Literal[StreamEventType.TEXT_DELTA] = StreamEventType.TEXT_DELTA
    text: str  # The text chunk
class ContentBlockStart(BaseStreamEvent):
    """Event signaling text content is complete"""
    type: Literal[StreamEventType.CONTENT_BLOCK_START] = StreamEventType.CONTENT_BLOCK_START
    content_type: Literal["text", "tool_call", "tool_result"]
    content_block: Dict[str, Any]

class ContentBlockEnd(BaseStreamEvent):
    """Event signaling text content is complete"""
    type: Literal[StreamEventType.CONTENT_BLOCK_END] = StreamEventType.CONTENT_BLOCK_END
class ThinkingDeltaEvent(BaseStreamEvent):
    """Event containing agent's thinking process"""
    type: Literal[StreamEventType.THINKING_DELTA] = StreamEventType.THINKING_DELTA
    thinking: str

class ToolCallEvent(BaseStreamEvent):
    """Event containing a tool call"""
    type: Literal[StreamEventType.TOOL_CALL] = StreamEventType.TOOL_CALL
    tool_call: ToolCall  # Reuse our ToolCall type

class ToolCallDeltaEvent(BaseStreamEvent):
    """Event containing a tool call"""
    type: Literal[StreamEventType.TOOL_CALL_DELTA] = StreamEventType.TOOL_CALL_DELTA
    arguments_delta: str

class ToolResultEvent(BaseStreamEvent):
    """Event containing a tool result"""
    type: Literal[StreamEventType.TOOL_RESULT] = StreamEventType.TOOL_RESULT
    tool_result: ToolResult  # Reuse our ToolResult type

class ErrorEvent(BaseStreamEvent):
    """Event containing an error"""
    type: Literal[StreamEventType.ERROR] = StreamEventType.ERROR
    error: str

class DoneEvent(BaseStreamEvent):
    """Event signaling stream completion"""
    type: Literal[StreamEventType.DONE] = StreamEventType.DONE

StreamEvent = Annotated[
    Union[
        StartEvent,
        ContentBlockStart,
        ContentBlockEnd,
        TextDeltaEvent,
        ThinkingDeltaEvent,
        ToolCallEvent,
        ToolCallDeltaEvent,
        ToolResultEvent,
        ErrorEvent,
        DoneEvent
    ],
    Discriminator('type')
]
    
    