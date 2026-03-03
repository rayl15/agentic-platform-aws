from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from agentic_platform.core.models.llm_models import LLMResponse, Usage
from agentic_platform.core.models.tool_models import ToolSpec
from agentic_platform.core.models.memory_models import ToolCall

class BaseLLMResponseConverter(ABC):
    """Abstract base class for LLM API provider converters"""

    @classmethod
    @abstractmethod
    def to_llm_response(cls, converse_response: Dict[str, Any]) -> LLMResponse:
        """Convert Bedrock converse response to LLMResponse"""
        pass

    @classmethod
    @abstractmethod
    def to_tool_spec_config(cls, tools: List[ToolSpec], force_tool: Optional[str] = None) -> Dict[str, Any]:
        """Convert tools to Bedrock tool spec config"""
        pass

##########################################################################
# Converter class to convert the converse response.
# This is a simplified version, but the value of owning your own types is
# that you can make it as complex or simple as you want!
##########################################################################

class ConverseResponseConverter(BaseLLMResponseConverter):
    """Converts Bedrock converse responses to standardized LLMResponse format."""
    
    @classmethod
    def to_llm_response(cls, converse_response: Dict[str, Any]) -> LLMResponse:
        """Convert Bedrock converse response to LLMResponse"""

        # Early return if no output or message
        if 'output' not in converse_response or 'message' not in converse_response['output']:
            return LLMResponse(raw_response=converse_response)
        
        output: Dict[str, Any] = converse_response['output']
        content_parts: List[Dict[str, Any]] = output['message'].get('content', [])
        
        # Extract text parts
        text_parts: List[str] = [part['text'] for part in content_parts if 'text' in part]
        message: str = ' '.join(text_parts)
        
        # Extract tool calls
        tool_calls: List[ToolCall] = [
            ToolCall(
                name=part['toolUse']['name'],
                arguments=part['toolUse']['input'],
                id=part['toolUse'].get('toolUseId')
            )
            for part in content_parts if 'toolUse' in part
        ]
        
        # Create usage object
        usage: Usage = Usage(
            prompt_tokens=converse_response.get('usage', {}).get('inputTokens', 0),
            completion_tokens=converse_response.get('usage', {}).get('outputTokens', 0),
            total_tokens=converse_response.get('usage', {}).get('totalTokens', 0)
        )
        
        return LLMResponse(
            id=converse_response.get('ResponseMetadata', {}).get('RequestId', ''),
            text=message,
            stop_reason=converse_response.get('stopReason'),
            tool_calls=tool_calls,
            usage=usage,
            raw_response=converse_response
        )
    
    @classmethod
    def to_tool_spec_config(cls, tools: List[ToolSpec], force_tool: Optional[str] = None) -> Dict[str, Any]:
        """
        Create tool configuration for Bedrock.

        force_tool forces the model to use a specific tool. This is useful for testing
        and or generating structured output.
        """

        # Iterate through tools and convert to Bedrock tool spec format.
        tools = [{
            "toolSpec": {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": {"json": tool.model.model_json_schema()}
            }
        } for tool in tools]
        
        # Create tool config like we did in module 1 notebook 6.
        tool_config = {
            "tools": tools,
            "toolChoice": {"tool": {"name": force_tool}} if force_tool else {"auto": {}}
        }
            
        return tool_config
