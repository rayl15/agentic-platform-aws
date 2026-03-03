from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from agentic_platform.core.models.memory_models import ToolCall, Message, ToolResult
from agentic_platform.core.models.tool_models import ToolSpec
######################################################
# Define new Output Type for Bedrock responses.
######################################################

class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class LLMResponse(BaseModel):
    id: str = None
    text: str = ""
    stop_reason: Optional[str] = None 
    tool_calls: List[ToolCall] = []
    usage: Usage = Usage()
    output: List[Message] = []
    raw_response: Dict[str, Any] = {} 

class LLMRequest(BaseModel):
    system_prompt: str
    messages: List[Message]
    model_id: str
    hyperparams: Dict[str, Any]
    tools: Optional[List[ToolSpec]] = None
    force_tool: Optional[str] = None

class LiteLLMClientInfo(BaseModel):
    api_key: str
    api_endpoint: str